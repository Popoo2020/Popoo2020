"""Connect offline provider exports to the bounded planning snapshot.

``snapshot_from_exports(scenario, subject_id, exports, captured_at)`` returns
``{"snapshot": ..., "evidence": ...}``. Pass only result["snapshot"] to
engine.make_plan; save evidence separately so assignment records retain the
engine's strict two-field schema.

The exports bundle has exactly these keys::

    {
      "schema_version": 1,
      "documents": {"azure": [envelope], "aws": [envelope, ...], "gcp": [envelope]},
      "coverage": [
        {"provider": "azure", "resource": "TENANT", "document_index": 0,
         "complete": true},
        {"provider": "aws", "resource": "ACCOUNT", "permission": "PERMISSION_SET_ARN",
         "document_index": 0, "complete": true},
        {"provider": "gcp", "resource": "RESOURCE", "document_index": 0,
         "complete": true}
      ]
    }

Every provider requires at least one document. The envelopes are documented in
providers.py. Coverage must name each catalogued Azure tenant and GCP resource,
and *every* catalogued AWS account/permission-set query, exactly once. Each
coverage row is bound to one document by its provider-local index. The coverage
set must equal the catalogue's query scope, not just the subject's desired role.
Extra documents, duplicate scopes, partial assertions and uncatalogued observed
assignments are rejected. An AWS empty response is meaningful only alongside
its explicit account/permission-set coverage assertion. Non-empty AWS responses
must agree with that assertion, including records for other USER principals.

This proves internal scope/identity consistency only. The collector asserts
query completeness and captured_at; this offline code does not authenticate
the source, prove that records were not omitted, or verify live account status.
``complete`` refers only to the declared catalogue of direct assignments.
``disabled_subjects=[]`` is an explicit simulation assumption in the evidence,
not a statement that any cloud account is actually enabled. No effective IAM
evaluation, inherited access calculation, cloud request or cloud mutation is
performed.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .common import PROVIDERS, digest, iso, required_text, timestamp
from .engine import validate_scenario, validate_snapshot
from .providers import normalize_aws, normalize_azure, normalize_gcp

__all__ = ["snapshot_from_exports"]

_NORMALIZERS = {"azure": normalize_azure, "aws": normalize_aws, "gcp": normalize_gcp}
_RESOURCE_FIELDS = {"azure": "tenant_id", "aws": "account_id", "gcp": "resource"}


def _object(value: Any, label: str) -> dict:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be a JSON object with string keys")
    return value


def _exact_keys(value: dict, expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ValueError(f"{label} must contain exactly: {', '.join(sorted(expected))}")


def _scope(provider: str, resource: str, permission: str | None = None) -> tuple:
    return (provider, resource, permission if provider == "aws" else None)


def _digest(value: Any, label: str) -> str:
    try:
        return digest(value)
    except (TypeError, ValueError, RecursionError) as error:
        raise ValueError(f"{label} must be finite, serializable JSON") from error


def snapshot_from_exports(scenario: dict, subject_id: str, exports: dict, captured_at: str) -> dict:
    """Validate explicit catalogue coverage, map direct assignments and retain evidence."""
    try:
        validate_scenario(scenario)
    except (AttributeError, KeyError, TypeError) as error:
        raise ValueError("Malformed scenario for provider import") from error
    required_text(subject_id, "Subject ID")
    if subject_id not in scenario["identities"]:
        raise ValueError("Import subject is not mapped in the scenario")
    captured_at = iso(timestamp(captured_at))
    exports = _object(exports, "exports")
    _exact_keys(exports, {"schema_version", "documents", "coverage"}, "exports")
    if type(exports["schema_version"]) is not int or exports["schema_version"] != 1:
        raise ValueError("Unsupported exports schema version")
    documents = _object(exports["documents"], "exports.documents")
    _exact_keys(documents, set(PROVIDERS), "exports.documents")
    external_ids = scenario["identities"][subject_id]["external_ids"]
    normalized = {}
    document_keys = set()
    for provider in sorted(PROVIDERS):
        provider_documents = documents[provider]
        if not isinstance(provider_documents, list) or not provider_documents:
            raise ValueError(f"exports.documents.{provider} must be a non-empty list")
        for index, document in enumerate(provider_documents):
            document = _object(document, f"exports.documents.{provider}[{index}]")
            # Validate the envelope identity before looking at results. Empty
            # results from the wrong account-holder are not evidence of absence.
            if document.get("principal_id") != external_ids[provider]:
                raise ValueError(
                    f"{provider} document {index} principal_id does not match "
                    f"the immutable external identity for {subject_id}"
                )
            key = (provider, index)
            normalized[key] = _NORMALIZERS[provider](document)
            document_keys.add(key)

    catalogue = scenario["policy"]["entitlements"]
    mappings = {
        (entry["provider"], entry["resource"], entry["permission"]): entitlement_id
        for entitlement_id, entry in catalogue.items()
    }
    expected_scopes = {
        _scope(entry["provider"], entry["resource"], entry["permission"])
        for entry in catalogue.values()
    }
    coverage = exports["coverage"]
    if not isinstance(coverage, list) or not coverage:
        raise ValueError("exports.coverage must explicitly assert complete query coverage")
    seen_scopes = set()
    covered_documents = set()
    coverage_evidence = []
    for index, raw_claim in enumerate(coverage):
        claim = _object(raw_claim, f"exports.coverage[{index}]")
        provider = claim.get("provider")
        if not isinstance(provider, str) or provider not in PROVIDERS:
            raise ValueError(f"exports.coverage[{index}] names an unknown provider")
        fields = {"provider", "resource", "document_index", "complete"}
        if provider == "aws":
            fields.add("permission")
        _exact_keys(claim, fields, f"exports.coverage[{index}]")
        resource = required_text(claim["resource"], "Coverage resource")
        permission = (
            required_text(claim["permission"], "Coverage permission") if provider == "aws" else None
        )
        if claim["complete"] is not True:
            raise ValueError("Every coverage row must explicitly assert complete=true")
        document_index = claim["document_index"]
        if type(document_index) is not int or document_index < 0:
            raise ValueError("Coverage document_index must be a non-negative integer")
        key = (provider, document_index)
        if key not in document_keys:
            raise ValueError("Coverage references a missing provider document")
        query_scope = _scope(provider, resource, permission)
        if query_scope in seen_scopes:
            raise ValueError("Duplicate provider query scope in coverage")
        if key in covered_documents:
            raise ValueError("A provider document cannot cover multiple query scopes")
        if query_scope not in expected_scopes:
            raise ValueError("Coverage query scope is outside the entitlement catalogue")
        document = documents[provider][document_index]
        if document[_RESOURCE_FIELDS[provider]] != resource:
            raise ValueError("Coverage resource does not match its provider document")
        if provider == "aws":
            for assignment in document["response"]["AccountAssignments"]:
                if assignment["PermissionSetArn"] != permission:
                    raise ValueError("AWS permission-set query coverage contradicts its response")
        seen_scopes.add(query_scope)
        covered_documents.add(key)
        coverage_evidence.append(
            {
                **deepcopy(claim),
                "document_ref": f"/documents/{provider}/{document_index}",
                "document_digest": _digest(document, "Provider document"),
            }
        )
    if seen_scopes != expected_scopes:
        raise ValueError(
            "Incomplete catalogue coverage: every catalogued provider query is required"
        )
    if covered_documents != document_keys:
        raise ValueError(
            "Every supplied provider document must have exactly one coverage assertion"
        )

    assignments = []
    assignment_evidence = []
    seen_entitlements = set()
    for provider, document_index in sorted(normalized):
        for record in normalized[(provider, document_index)]:
            binding = (provider, record["resource"], record["entitlement_id"])
            if binding not in mappings:
                raise ValueError(
                    "Observed provider assignment has no catalogue mapping: "
                    f"{provider}/{record['resource']}/{record['entitlement_id']}"
                )
            entitlement_id = mappings[binding]
            if entitlement_id in seen_entitlements:
                raise ValueError("An entitlement was observed in more than one query scope")
            seen_entitlements.add(entitlement_id)
            assignments.append({"subject_id": subject_id, "entitlement_id": entitlement_id})
            pointer = record["source_ref"].partition("#")[2]
            assignment_evidence.append(
                {
                    "subject_id": subject_id,
                    "entitlement_id": entitlement_id,
                    "provider": provider,
                    "principal_id": record["principal_id"],
                    "resource": record["resource"],
                    "permission": record["entitlement_id"],
                    "source_ref": record["source_ref"],
                    "export_ref": f"/documents/{provider}/{document_index}{pointer}",
                }
            )
    assignments.sort(key=lambda assignment: assignment["entitlement_id"])
    assignment_evidence.sort(key=lambda assignment: assignment["entitlement_id"])
    coverage_evidence.sort(
        key=lambda claim: (claim["provider"], claim["resource"], claim.get("permission", ""))
    )
    snapshot = {
        "schema_version": 1,
        "captured_at": captured_at,
        "scope": "catalogued_direct_assignments",
        "complete": {provider: True for provider in sorted(PROVIDERS)},
        "subjects": [subject_id],
        "disabled_subjects": [],
        "assignments": assignments,
    }
    validate_snapshot(scenario, snapshot, subject_id, scenario["as_of"])
    evidence = {
        "schema_version": 1,
        "subject_id": subject_id,
        "captured_at": captured_at,
        "scope": "catalogued_direct_assignments",
        "snapshot_digest": _digest(snapshot, "Snapshot"),
        "catalogue_digest": _digest(catalogue, "Entitlement catalogue"),
        "identity_bindings_digest": _digest(external_ids, "External identity bindings"),
        "exports_digest": _digest(exports, "Exports bundle"),
        "coverage": coverage_evidence,
        "assignments": assignment_evidence,
        "source_authenticated": False,
        "actual_collection_completeness_verified": False,
        "assumptions": [
            "The collector asserts every listed query was fully collected at captured_at.",
            "disabled_subjects=[] is a simulation assumption; live account-enabled state is unknown.",
        ],
        "limitations": [
            "Coverage checks establish catalogue-scope consistency, not source authority or authenticity.",
            "The snapshot contains direct assignments only; it does not establish effective access.",
        ],
    }
    return {"snapshot": snapshot, "evidence": evidence}
