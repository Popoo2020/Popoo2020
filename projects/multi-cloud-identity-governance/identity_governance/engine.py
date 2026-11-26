"""Plan changes to a bounded set of access assignments and simulate their execution.

All identities, approvals and execution outcomes in the bundled demo are synthetic.
Approver names are policy assertions supplied by the caller, not authenticated users.
The engine has no cloud clients and cannot grant or revoke real access.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
from typing import Any

from .common import PROVIDERS, digest, iso, object_keys, required_text, timestamp

EVENT_KINDS = frozenset({"joiner", "mover", "leaver", "contract_expiry", "access_review"})


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    for item in value:
        required_text(item, label)
    if len(set(value)) != len(value):
        raise ValueError(f"{label} must not contain duplicates")
    return value


def validate_scenario(scenario: dict[str, Any]) -> None:
    object_keys(
        scenario,
        {"schema_version", "as_of", "policy", "identities", "snapshot", "events"},
        {"company"},
        "Scenario",
    )
    if (
        not isinstance(scenario, dict)
        or type(scenario.get("schema_version")) is not int
        or scenario.get("schema_version") != 1
    ):
        raise ValueError("Unsupported scenario schema")
    policy = scenario.get("policy", {})
    object_keys(
        policy,
        {
            "entitlements",
            "roles",
            "approvers",
            "conflicts",
            "snapshot_max_age_minutes",
            "plan_valid_minutes",
        },
        set(),
        "Policy",
    )
    identities = scenario.get("identities", {})
    entitlements = policy.get("entitlements", {})
    roles = policy.get("roles", {})
    approvers = policy.get("approvers", [])
    if not all(isinstance(value, dict) for value in (identities, entitlements, roles)):
        raise ValueError("Identities, entitlements and roles must be objects")
    if not identities or not entitlements or not roles or not isinstance(approvers, list):
        raise ValueError("Identities, entitlements, roles and approvers are required")
    _strings(approvers, "Approvers")
    bindings = set()
    for entitlement_id, entry in entitlements.items():
        object_keys(
            entry,
            {"provider", "resource", "permission", "label", "owner", "authority"},
            set(),
            "Entitlement",
        )
        required_text(entitlement_id, "Entitlement ID")
        required_text(entry["provider"], "Provider")
        if entry.get("provider") not in PROVIDERS:
            raise ValueError(f"Unknown provider for {entitlement_id}")
        for field in ("resource", "permission", "owner", "authority", "label"):
            required_text(entry.get(field), f"{entitlement_id}.{field}")
        if entry["owner"] not in approvers:
            raise ValueError(f"Unrecognised resource owner for {entitlement_id}")
        if entry["authority"] not in {"idp", "provider"}:
            raise ValueError("Authority must be idp or provider")
        binding = (entry["provider"], entry["resource"], entry["permission"])
        if binding in bindings:
            raise ValueError("Duplicate provider/resource/permission mapping")
        bindings.add(binding)
    for role, desired in roles.items():
        required_text(role, "Role")
        _strings(desired, f"Role {role}")
        if set(desired) - set(entitlements):
            raise ValueError(f"Unknown entitlement in role {role}")
    for identity_id, identity in identities.items():
        object_keys(
            identity, {"kind", "status", "role", "manager", "external_ids"}, {"end_at"}, "Identity"
        )
        required_text(identity_id, "Identity ID")
        for field in ("kind", "status", "role", "manager"):
            required_text(identity[field], f"Identity.{field}")
        if identity.get("kind") not in {"employee", "contractor"}:
            raise ValueError(f"Unsupported workforce identity kind: {identity_id}")
        if identity.get("status") not in {"active", "departed"}:
            raise ValueError(f"Unknown employment status: {identity_id}")
        if identity.get("role") not in roles or identity.get("manager") not in approvers:
            raise ValueError(f"Missing role or recognised manager for {identity_id}")
        if (
            not isinstance(identity.get("external_ids"), dict)
            or set(identity["external_ids"]) != PROVIDERS
        ):
            raise ValueError(f"Explicit immutable identity bindings required: {identity_id}")
        for external_id in identity["external_ids"].values():
            required_text(external_id, "External identity ID")
        if identity["kind"] == "contractor":
            timestamp(identity.get("end_at"))
    for provider in PROVIDERS:
        ids = [person["external_ids"][provider] for person in identities.values()]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Ambiguous identity mapping for {provider}")
    if not isinstance(policy["conflicts"], list):
        raise ValueError("Conflicts must be a list")
    for pair in policy["conflicts"]:
        _strings(pair, "Separation-of-duties rule")
        if len(pair) != 2:
            raise ValueError("A separation-of-duties rule must name two distinct entitlements")
        if set(pair) - set(entitlements):
            raise ValueError("Unknown entitlement in a separation-of-duties rule")
    for field in ("snapshot_max_age_minutes", "plan_valid_minutes"):
        if type(policy.get(field)) is not int or not 0 < policy[field] <= 1440:
            raise ValueError(f"{field} must be an integer from 1 to 1440")
    timestamp(scenario.get("as_of"))
    if not isinstance(scenario["events"], dict):
        raise ValueError("Events must be an object")
    for name, event in scenario["events"].items():
        required_text(name, "Event name")
        object_keys(
            event,
            {"event_id", "kind", "subject_id", "effective_at", "source"},
            {"target_role"},
            "Event",
        )
        for field in ("event_id", "kind", "subject_id", "source"):
            required_text(event[field], f"Event.{field}")
        timestamp(event["effective_at"])


def validate_snapshot(
    scenario: dict[str, Any], snapshot: dict[str, Any], subject: str, now: str
) -> None:
    object_keys(
        snapshot,
        {
            "schema_version",
            "captured_at",
            "scope",
            "complete",
            "subjects",
            "assignments",
            "disabled_subjects",
        },
        set(),
        "Snapshot",
    )
    if (
        not isinstance(snapshot, dict)
        or type(snapshot.get("schema_version")) is not int
        or snapshot.get("schema_version") != 1
    ):
        raise ValueError("Unsupported snapshot schema")
    if snapshot.get("scope") != "catalogued_direct_assignments":
        raise ValueError("Only an explicit, bounded assignment scope is supported")
    completeness = snapshot.get("complete", {})
    if (
        not isinstance(completeness, dict)
        or set(completeness) != PROVIDERS
        or any(value is not True for value in completeness.values())
    ):
        raise ValueError("Incomplete provider snapshot: missing data is not evidence of no access")
    subjects = snapshot.get("subjects", [])
    _strings(subjects, "Snapshot subjects")
    if subject not in subjects:
        raise ValueError("Snapshot does not cover the requested subject")
    if set(subjects) - set(scenario["identities"]):
        raise ValueError("Unknown identity in snapshot scope")
    age = timestamp(now) - timestamp(snapshot.get("captured_at"))
    if age < timedelta(0) or age > timedelta(
        minutes=scenario["policy"]["snapshot_max_age_minutes"]
    ):
        raise ValueError("Snapshot is stale or dated in the future")
    assignments = snapshot.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("Snapshot assignments must be a list")
    seen = set()
    for grant in assignments:
        if not isinstance(grant, dict) or set(grant) != {"subject_id", "entitlement_id"}:
            raise ValueError("Malformed assignment record")
        required_text(grant["subject_id"], "Assignment subject")
        required_text(grant["entitlement_id"], "Assignment entitlement")
        if (
            grant["subject_id"] not in subjects
            or grant["entitlement_id"] not in scenario["policy"]["entitlements"]
        ):
            raise ValueError("Assignment is outside the declared subject or entitlement scope")
        key = (grant["subject_id"], grant["entitlement_id"])
        if key in seen:
            raise ValueError("Duplicate assignment in snapshot")
        seen.add(key)
    disabled = snapshot.get("disabled_subjects", [])
    _strings(disabled, "Disabled subjects")
    if set(disabled) - set(subjects):
        raise ValueError("Invalid disabled-subject scope")


def access_for(snapshot: dict[str, Any], subject: str) -> set[str]:
    return {
        item["entitlement_id"] for item in snapshot["assignments"] if item["subject_id"] == subject
    }


def conflicts_for(policy: dict[str, Any], entitlements: set[str]) -> list[list[str]]:
    return [pair for pair in policy.get("conflicts", []) if set(pair) <= entitlements]


def _operation(
    event: dict[str, Any], action: str, entitlement_id: str, metadata: dict[str, Any]
) -> dict[str, Any]:
    return {
        "operation_id": digest([event["event_id"], event["subject_id"], action, entitlement_id])[
            :24
        ],
        "action": action,
        "subject_id": event["subject_id"],
        "entitlement_id": entitlement_id,
        "provider": metadata["provider"],
        "resource": metadata["resource"],
        "permission": metadata["permission"],
        "authority": metadata["authority"],
        "owner": metadata["owner"],
        "reason": "No longer justified by the authoritative workforce record"
        if action == "revoke"
        else "Required by the approved target role",
    }


def make_plan(
    scenario: dict[str, Any], event_name: str, snapshot: dict[str, Any] | None = None
) -> dict[str, Any]:
    validate_scenario(scenario)
    if event_name not in scenario.get("events", {}):
        raise ValueError(f"Unknown event: {event_name}")
    event = scenario["events"][event_name]
    if event.get("kind") not in EVENT_KINDS or event.get("source") != "authoritative_hr_fixture":
        raise ValueError("Unsupported event kind or source")
    required_text(event.get("event_id"), "Event ID")
    subject = event.get("subject_id")
    if subject not in scenario["identities"]:
        raise ValueError("Unmapped identity; email matching is not an identity binding")
    if timestamp(event.get("effective_at")) > timestamp(scenario["as_of"]):
        raise ValueError("Event is not yet effective")
    snapshot = deepcopy(snapshot if snapshot is not None else scenario["snapshot"])
    now = scenario["as_of"]
    validate_snapshot(scenario, snapshot, subject, now)
    identity = scenario["identities"][subject]
    policy = scenario["policy"]
    expired = identity["kind"] == "contractor" and timestamp(identity["end_at"]) <= timestamp(now)
    departed = identity["status"] == "departed"
    if event["kind"] == "leaver" and not departed:
        raise ValueError("Leaver event conflicts with authoritative employment status")
    if event["kind"] == "contract_expiry" and not expired:
        raise ValueError("Contract expiry is not established by the workforce record")
    if event.get("target_role", identity["role"]) != identity["role"]:
        raise ValueError("Event target role conflicts with the authoritative workforce record")
    disable = expired or departed
    desired = set() if disable else set(policy["roles"][identity["role"]])
    if conflicts_for(policy, desired):
        raise ValueError("Target role violates separation of duties")
    current = access_for(snapshot, subject)
    removals = sorted(current - desired)
    additions = (
        sorted(desired - current) if event["kind"] in {"joiner", "mover"} and not disable else []
    )
    if subject in snapshot.get("disabled_subjects", []) and additions:
        raise ValueError("Disabled identity cannot receive new assignments")
    operations = []
    if disable and subject not in snapshot.get("disabled_subjects", []):
        operations.append(
            {
                "operation_id": digest([event["event_id"], subject, "disable_identity"])[:24],
                "action": "disable_identity",
                "subject_id": subject,
                "entitlement_id": None,
                "provider": "azure",
                "resource": "authoritative_identity_provider",
                "permission": identity["external_ids"]["azure"],
                "authority": "idp",
                "owner": identity["manager"],
                "reason": "Authoritative departure or contract expiry",
            }
        )
    operations.extend(
        _operation(event, "revoke", item, policy["entitlements"][item]) for item in removals
    )
    operations.extend(
        _operation(event, "grant", item, policy["entitlements"][item]) for item in additions
    )
    plan = {
        "schema_version": 1,
        "mode": "simulation_only",
        "scope": "catalogued_direct_assignments",
        "event_name": event_name,
        "event": deepcopy(event),
        "subject_id": subject,
        "created_at": now,
        "expires_at": iso(timestamp(now) + timedelta(minutes=policy["plan_valid_minutes"])),
        "snapshot_digest": digest(snapshot),
        "policy_digest": digest(policy),
        "identity_digest": digest(identity),
        "manager": identity["manager"],
        "desired_entitlements": sorted(desired),
        "operations": operations,
        "control_ids": ["IG-01", "IG-02", "IG-03", "IG-04", "IG-05", "IG-06"],
    }
    plan["plan_id"] = digest(plan)
    return plan


def demo_approvals(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Create visibly synthetic approvals for demo grants, never for a live service."""
    result = []
    for operation in plan["operations"]:
        if operation["action"] != "grant":
            continue
        for approver in sorted({plan["manager"], operation["owner"]}):
            result.append(
                {
                    "plan_id": plan["plan_id"],
                    "operation_id": operation["operation_id"],
                    "subject_id": plan["subject_id"],
                    "approver_id": approver,
                    "decision": "approve",
                    "approved_at": plan["created_at"],
                    "expires_at": plan["expires_at"],
                    "source": "synthetic_demo",
                }
            )
    return result


def _approval_check(
    plan: dict[str, Any], operation: dict[str, Any], approvals: list[dict[str, Any]], now: str
) -> tuple[bool, str]:
    required = {plan["manager"], operation["owner"]}
    if len(required) != 2:
        return False, "Manager and resource owner must be two distinct approvers"
    accepted = set()
    for approval in approvals:
        if not isinstance(approval, dict):
            return False, "Malformed approval"
        if approval.get("operation_id") != operation["operation_id"]:
            continue
        if (
            approval.get("plan_id") != plan["plan_id"]
            or approval.get("subject_id") != plan["subject_id"]
        ):
            return False, "Approval is not bound to this plan and subject"
        approver = approval.get("approver_id")
        if approver == plan["subject_id"] or approver not in required:
            return False, "Self-approval or unrecognised approver"
        if approval.get("decision") != "approve":
            return False, "Approval explicitly denied or invalid"
        try:
            approved_at = timestamp(approval.get("approved_at"))
            expires_at = timestamp(approval.get("expires_at"))
        except ValueError:
            return False, "Invalid approval timestamp"
        if (
            not timestamp(plan["created_at"])
            <= approved_at
            <= timestamp(now)
            < expires_at
            <= timestamp(plan["expires_at"])
        ):
            return False, "Approval expired, future-dated or outside plan validity"
        if approver in accepted:
            return False, "Duplicate approval by the same person"
        accepted.add(approver)
    if accepted != required:
        return False, "Manager and resource-owner approval required"
    return True, "Bound, unexpired demo approvals present; identities are not authenticated"


def simulate(
    scenario: dict[str, Any],
    plan: dict[str, Any],
    approvals: list[dict[str, Any]],
    *,
    snapshot: dict[str, Any] | None = None,
    fail_operations: set[str] | None = None,
) -> dict[str, Any]:
    """Apply a verified plan to an in-memory snapshot; never calls a cloud API."""
    validate_scenario(scenario)
    snapshot = deepcopy(snapshot if snapshot is not None else scenario["snapshot"])
    now = scenario["as_of"]
    validate_snapshot(scenario, snapshot, plan.get("subject_id"), now)
    payload = {key: value for key, value in plan.items() if key != "plan_id"}
    if plan.get("plan_id") != digest(payload):
        raise ValueError("Plan integrity check failed")
    if not timestamp(plan["created_at"]) <= timestamp(now) < timestamp(plan["expires_at"]):
        raise ValueError("Plan expired or future-dated")
    if plan["snapshot_digest"] != digest(snapshot):
        raise ValueError("Snapshot changed; produce a new plan before execution")
    if plan["policy_digest"] != digest(scenario["policy"]):
        raise ValueError("Policy changed; previous approvals no longer apply")
    if plan["identity_digest"] != digest(scenario["identities"][plan["subject_id"]]):
        raise ValueError("Workforce record changed; produce a new plan")
    identity = scenario["identities"][plan["subject_id"]]
    if identity["kind"] == "contractor" and timestamp(plan["created_at"]) < timestamp(
        identity["end_at"]
    ) <= timestamp(now):
        raise ValueError(
            "Contract expired after planning; replan even when the earlier plan was a no-op"
        )
    # Re-derive authorised operations: a recomputed hash alone does not authorise a forged plan.
    replay_scenario = deepcopy(scenario)
    replay_scenario["as_of"] = plan["created_at"]
    expected = make_plan(replay_scenario, plan["event_name"], snapshot)
    if expected != plan:
        raise ValueError("Plan differs from the policy-derived operations")
    if not isinstance(approvals, list):
        raise ValueError("Approvals must be a list")
    for approval in approvals:
        object_keys(
            approval,
            {
                "plan_id",
                "operation_id",
                "subject_id",
                "approver_id",
                "decision",
                "approved_at",
                "expires_at",
                "source",
            },
            set(),
            "Approval",
        )
        if approval["source"] != "synthetic_demo":
            raise ValueError("This local simulator accepts only explicitly synthetic approvals")
    failed = fail_operations or set()
    known_operations = {item["operation_id"] for item in plan["operations"]}
    if failed - known_operations:
        raise ValueError("Failure injection references an unknown operation")
    state = deepcopy(snapshot)
    state.setdefault("disabled_subjects", [])
    operation_results = []
    audit: list[dict[str, Any]] = []
    removal_failed = False

    def record(event_type: str, details: dict[str, Any]) -> None:
        event = {
            "sequence": len(audit) + 1,
            "at": now,
            "event_type": event_type,
            "plan_id": plan["plan_id"],
            "subject_id": plan["subject_id"],
            "details": details,
            "previous_hash": audit[-1]["hash"] if audit else "0" * 64,
        }
        event["hash"] = digest(event)
        audit.append(event)

    record("plan_validated", {"mode": "simulation_only", "snapshot_digest": digest(snapshot)})
    for operation in plan["operations"]:
        action = operation["action"]
        status = "simulated"
        reason = operation["reason"]
        if action == "grant":
            allowed, approval_reason = _approval_check(plan, operation, approvals, now)
            proposed = access_for(state, plan["subject_id"]) | {operation["entitlement_id"]}
            if removal_failed:
                status, reason = (
                    "blocked",
                    "A removal or identity-disable operation failed; all new grants are frozen",
                )
            elif not allowed:
                status, reason = "blocked", approval_reason
            elif conflicts_for(scenario["policy"], proposed):
                status, reason = "blocked", "Resulting state violates separation of duties"
            else:
                reason = approval_reason
        if status == "simulated" and operation["operation_id"] in failed:
            status, reason = (
                "failed",
                "Injected provider failure; no provider operation was attempted",
            )
            if action in {"revoke", "disable_identity"}:
                removal_failed = True
        if status == "simulated":
            if action == "disable_identity":
                state["disabled_subjects"] = sorted(
                    set(state["disabled_subjects"]) | {plan["subject_id"]}
                )
            elif action == "revoke":
                state["assignments"] = [
                    grant
                    for grant in state["assignments"]
                    if not (
                        grant["subject_id"] == plan["subject_id"]
                        and grant["entitlement_id"] == operation["entitlement_id"]
                    )
                ]
            elif action == "grant":
                state["assignments"].append(
                    {
                        "subject_id": plan["subject_id"],
                        "entitlement_id": operation["entitlement_id"],
                    }
                )
        outcome = {**operation, "status": status, "result_reason": reason}
        operation_results.append(outcome)
        record("operation_evaluated", outcome)
    state["assignments"] = sorted(
        state["assignments"], key=lambda item: (item["subject_id"], item["entitlement_id"])
    )
    # Local simulation does not refresh the observation time, including for untouched subjects.
    denied = any(item["status"] != "simulated" for item in operation_results)
    changed = any(item["status"] == "simulated" for item in operation_results)
    status = (
        "partial_simulation"
        if denied and changed
        else "blocked_simulation"
        if denied
        else "completed_simulation"
    )
    remaining = access_for(state, plan["subject_id"])
    unexpected = sorted(remaining - set(plan["desired_entitlements"]))
    missing = sorted(set(plan["desired_entitlements"]) - remaining)
    review = {
        "unexpected_assignments": unexpected,
        "missing_role_assignments": missing,
        "separation_of_duties_conflicts": conflicts_for(scenario["policy"], remaining),
        "catalogued_assignment_target_reached": not unexpected and not missing,
        "live_access_verified": False,
        "session_revocation_verified": False,
    }
    record("reconciliation_completed", {"status": status, "review": review})
    return {
        "schema_version": 1,
        "mode": "simulation_only",
        "status": status,
        "plan_id": plan["plan_id"],
        "subject_id": plan["subject_id"],
        "before": snapshot,
        "after": state,
        "operations": operation_results,
        "review": review,
        "audit": audit,
    }
