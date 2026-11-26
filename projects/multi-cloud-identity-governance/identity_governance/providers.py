"""Offline adapters for a deliberately small subset of provider JSON exports.

These functions normalize *explicit assignments*, not effective permissions.
They do not call a cloud API, authenticate a document, expand a group, evaluate
a condition, or modify identity/SCIM data. The caller is responsible for the
authenticity, collection scope and freshness of the supplied export. In
particular, a missing pagination token cannot prove that a collector did not
discard earlier pages. An empty result means no supported direct assignment in
this snapshot; it never proves that a person has no access.

Envelopes (all IDs below are strings):

* Azure: ``{"principal_id": "...", "tenant_id": "...", "groups":
  {"value": [{"id": "...", "@odata.type": "#microsoft.graph.group"}]}}``.
  ``groups`` is the complete, group-only response from the user's direct
  ``memberOf`` relationship, optionally cast to ``microsoft.graph.group``.
  A group ID becomes the entitlement; the tenant ID becomes the resource.
  Expanded/nested relationships, transitive exports, non-group objects and
  unfinished pagination are rejected. Ordinary group metadata is ignored.

* AWS: ``{"principal_id": "...", "account_id": "123456789012", "response":
  {"AccountAssignments": [{"AccountId": "123456789012", "PermissionSetArn":
  "arn:aws:sso:::permissionSet/ssoins-0123456789abcdef/ps-0123456789abcdef",
  "PrincipalType": "USER", "PrincipalId": "..."}]}}``. ``response`` is one
  complete ListAccountAssignments result for one account/permission set.
  Known other USER principals are ignored. Any GROUP, inconsistent account,
  mixed permission sets or unfinished pagination fails the entire snapshot.
  The permission-set ARN is the entitlement; AccountId is the resource.

* GCP: ``{"principal_id": "user:person@example.invalid", "resource":
  "projects/example-project", "policy": {"version": 1, "etag": "AQ==",
  "bindings": [{"role": "roles/viewer", "members":
  ["user:person@example.invalid"]}]}}``. ``policy`` is the resource's own
  getIamPolicy allow policy; explicitly include version 1 or 3 and its etag.
  Collect with requestedPolicyVersion=3 so conditions are not obscured.
  Only exact user, serviceAccount, and single workforce/workload principal://
  strings are supported. Known other individual principals are ignored.
  Conditions (including legacy _withcond_ role suffixes), groups, domains,
  public/wildcard/principalSet membership, deleted/unknown principal forms and
  inherited/effective-policy envelopes are rejected, even in other bindings.
  Deny policies, principal access boundaries, ancestor policies and role
  permission expansion are outside this contract. auditConfigs are ignored
  after checking their container shape; they are not access bindings.

Every result is a new dict with exactly provider, principal_id, entitlement_id,
resource and source_ref. source_ref is a local snapshot reference: a quoted
provider/scope prefix followed by a JSON Pointer fragment into the envelope.
It is not a live API URL or proof of collection. Duplicate assignments retain
the first occurrence's source_ref, in input order. Inputs are never mutated.
Malformed or unsupported documents raise ValueError, without partial output.

Provider references (checked 2026-11-26):
https://learn.microsoft.com/en-us/graph/api/user-list-memberof?view=graph-rest-1.0
https://docs.aws.amazon.com/singlesignon/latest/APIReference/API_ListAccountAssignments.html
https://docs.cloud.google.com/iam/docs/reference/rest/v1/Policy
https://docs.cloud.google.com/iam/docs/principal-identifiers
https://docs.cloud.google.com/iam/docs/allow-policies#specifying_a_policy_version_when_getting_a_policy
"""

from __future__ import annotations

import base64
import binascii
import re
from urllib.parse import quote

__all__ = ["normalize_azure", "normalize_aws", "normalize_gcp"]

_AWS_PERMISSION_SET = re.compile(
    r"arn:aws(?:-[a-z]{1,5}){0,3}:sso:::permissionSet/"
    r"(?:sso)?ins-[a-zA-Z0-9.-]{16}/ps-[a-zA-Z0-9./-]{16}"
)
_GCP_ROLE = re.compile(
    r"(?:roles/[a-zA-Z0-9_.]+|(?:projects|organizations)/"
    r"[a-zA-Z0-9._-]+/roles/[a-zA-Z0-9_.]+)"
)
_GCP_INDIVIDUAL = re.compile(r"(?:user|serviceAccount):[^\s:@/]+@[^\s:@/]+")
_GCP_FEDERATED = re.compile(
    r"principal://iam\.googleapis\.com/"
    r"(?:locations/global/workforcePools/[^/?#\s]+|"
    r"projects/[0-9]+/locations/global/workloadIdentityPools/[^/?#\s]+)"
    r"/subject/[^\s?#]+"
)
_AZURE_RELATIONSHIPS = {
    "members",
    "memberOf",
    "transitiveMembers",
    "transitiveMemberOf",
    "parentGroups",
    "inherited",
    "inheritedFrom",
    "condition",
    "conditions",
    "appRoleAssignments",
    "roleAssignments",
    "@removed",
}


def _object(value: object, path: str) -> dict:
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise ValueError(f"{path} must be a JSON object with string keys")
    return value


def _keys(value: dict, required: set[str], optional: set[str], path: str) -> None:
    missing = required.difference(value)
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(sorted(missing))}")
    extra = value.keys() - required - optional
    if extra:
        raise ValueError(f"{path} has unsupported fields: {', '.join(sorted(extra))}")


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{path} must be a non-empty string without outer whitespace")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{path} must not contain control characters")
    return value


def _array(value: object, path: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{path} must be a JSON array")
    return value


def _pagination(value: dict, name: str, path: str) -> None:
    if name not in value or value[name] is None or value[name] == "":
        return
    _string(value[name], f"{path}.{name}")
    raise ValueError(f"{path}.{name} indicates incomplete pagination; provide all pages")


def _record(provider: str, principal: str, entitlement: str, resource: str, pointer: str) -> dict:
    scope = f"{provider}:{quote(resource, safe='')}:{quote(principal, safe='')}"
    return {
        "provider": provider,
        "principal_id": principal,
        "entitlement_id": entitlement,
        "resource": resource,
        "source_ref": f"{scope}#{pointer}",
    }


def _deduplicate(records: list[dict]) -> list[dict]:
    seen: set[tuple[str, str, str, str]] = set()
    unique = []
    for record in records:
        key = tuple(
            record[field] for field in ("provider", "principal_id", "entitlement_id", "resource")
        )
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique


def normalize_azure(document: dict) -> list[dict]:
    """Normalize a complete direct Entra user-to-group membership snapshot."""
    document = _object(document, "azure")
    _keys(document, {"principal_id", "tenant_id", "groups"}, set(), "azure")
    principal = _string(document["principal_id"], "azure.principal_id")
    tenant = _string(document["tenant_id"], "azure.tenant_id")
    groups = _object(document["groups"], "azure.groups")
    _keys(groups, {"value"}, {"@odata.context", "@odata.count", "@odata.nextLink"}, "azure.groups")
    _pagination(groups, "@odata.nextLink", "azure.groups")
    if "@odata.context" in groups:
        context = _string(groups["@odata.context"], "azure.groups.@odata.context")
        if "transitive" in context.lower():
            raise ValueError("azure.groups contains unsupported transitive memberships")
    values = _array(groups["value"], "azure.groups.value")
    if "@odata.count" in groups:
        count = groups["@odata.count"]
        if type(count) is not int or count != len(values):
            raise ValueError("azure.groups.@odata.count must equal the complete value length")
    records = []
    for index, item in enumerate(values):
        path = f"azure.groups.value[{index}]"
        group = _object(item, path)
        entitlement = _string(group.get("id"), f"{path}.id")
        if group.get("@odata.type") != "#microsoft.graph.group":
            raise ValueError(f"{path} must explicitly be #microsoft.graph.group")
        if _AZURE_RELATIONSHIPS.intersection(group) or any(
            key.endswith("@odata.nextLink") for key in group
        ):
            raise ValueError(f"{path} contains unsupported nested, inherited or delta data")
        records.append(_record("azure", principal, entitlement, tenant, f"/groups/value/{index}"))
    return _deduplicate(records)


def normalize_aws(document: dict) -> list[dict]:
    """Normalize direct USER assignments in one complete ListAccountAssignments result."""
    document = _object(document, "aws")
    _keys(document, {"principal_id", "account_id", "response"}, set(), "aws")
    principal = _string(document["principal_id"], "aws.principal_id")
    account = _string(document["account_id"], "aws.account_id")
    if not re.fullmatch(r"[0-9]{12}", account):
        raise ValueError("aws.account_id must contain exactly 12 ASCII digits")
    response = _object(document["response"], "aws.response")
    _keys(response, {"AccountAssignments"}, {"NextToken", "ResponseMetadata"}, "aws.response")
    _pagination(response, "NextToken", "aws.response")
    if "ResponseMetadata" in response:
        metadata = _object(response["ResponseMetadata"], "aws.response.ResponseMetadata")
        if "HTTPStatusCode" in metadata:
            status = metadata["HTTPStatusCode"]
            if type(status) is not int or status != 200:
                raise ValueError("aws.response.ResponseMetadata reports a non-success response")
    values = _array(response["AccountAssignments"], "aws.response.AccountAssignments")
    records = []
    permission_set = None
    for index, item in enumerate(values):
        path = f"aws.response.AccountAssignments[{index}]"
        assignment = _object(item, path)
        _keys(
            assignment,
            {"AccountId", "PermissionSetArn", "PrincipalType", "PrincipalId"},
            set(),
            path,
        )
        if assignment["PrincipalType"] != "USER":
            raise ValueError(
                f"{path}.PrincipalType must be USER; unresolved GROUPs are unsupported"
            )
        assigned_account = _string(assignment["AccountId"], f"{path}.AccountId")
        if assigned_account != account:
            raise ValueError(f"{path}.AccountId does not match aws.account_id")
        entitlement = _string(assignment["PermissionSetArn"], f"{path}.PermissionSetArn")
        if not _AWS_PERMISSION_SET.fullmatch(entitlement):
            raise ValueError(f"{path}.PermissionSetArn is not a supported permission-set ARN")
        if permission_set is not None and permission_set != entitlement:
            raise ValueError("aws.response mixes permission sets; provide one API result at a time")
        permission_set = entitlement
        assigned_principal = _string(assignment["PrincipalId"], f"{path}.PrincipalId")
        if assigned_principal == principal:
            records.append(
                _record(
                    "aws", principal, entitlement, account, f"/response/AccountAssignments/{index}"
                )
            )
    return _deduplicate(records)


def _gcp_principal(value: object, path: str) -> str:
    principal = _string(value, path)
    if "*" in principal or not (
        _GCP_INDIVIDUAL.fullmatch(principal) or _GCP_FEDERATED.fullmatch(principal)
    ):
        raise ValueError(
            f"{path} is not a supported individual principal; "
            "groups, domains, public, deleted and principalSet forms are unsupported"
        )
    return principal


def normalize_gcp(document: dict) -> list[dict]:
    """Normalize exact, unconditional individual bindings on one GCP resource."""
    document = _object(document, "gcp")
    _keys(document, {"principal_id", "resource", "policy"}, set(), "gcp")
    principal = _gcp_principal(document["principal_id"], "gcp.principal_id")
    resource = _string(document["resource"], "gcp.resource")
    policy = _object(document["policy"], "gcp.policy")
    _keys(policy, {"version", "etag", "bindings"}, {"auditConfigs"}, "gcp.policy")
    if type(policy["version"]) is not int or policy["version"] not in (1, 3):
        raise ValueError("gcp.policy.version must explicitly be 1 or 3")
    etag = _string(policy["etag"], "gcp.policy.etag")
    try:
        if not base64.b64decode(etag, validate=True):
            raise ValueError("gcp.policy.etag must encode a non-empty value")
    except (ValueError, binascii.Error) as error:
        raise ValueError("gcp.policy.etag must be valid non-empty base64") from error
    if "auditConfigs" in policy:
        for index, config in enumerate(_array(policy["auditConfigs"], "gcp.policy.auditConfigs")):
            _object(config, f"gcp.policy.auditConfigs[{index}]")
    bindings = _array(policy["bindings"], "gcp.policy.bindings")
    records = []
    for index, item in enumerate(bindings):
        path = f"gcp.policy.bindings[{index}]"
        binding = _object(item, path)
        if "condition" in binding:
            raise ValueError(f"{path} contains an unsupported conditional binding")
        _keys(binding, {"role", "members"}, set(), path)
        role = _string(binding["role"], f"{path}.role")
        if "_withcond_" in role:
            raise ValueError(f"{path}.role hides a condition; export with requestedPolicyVersion=3")
        if not _GCP_ROLE.fullmatch(role):
            raise ValueError(f"{path}.role is not a supported predefined or custom role name")
        members = _array(binding["members"], f"{path}.members")
        if not members:
            raise ValueError(f"{path}.members must contain at least one principal")
        for member_index, member in enumerate(members):
            member = _gcp_principal(member, f"{path}.members[{member_index}]")
            if member == principal:
                records.append(
                    _record(
                        "gcp",
                        principal,
                        role,
                        resource,
                        f"/policy/bindings/{index}/members/{member_index}",
                    )
                )
    return _deduplicate(records)
