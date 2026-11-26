"""Readable review reports and verifiable local evidence bundles.

Checksums detect changes relative to the accompanying manifest. The manifest is
not independently signed: an actor able to rewrite every file can rewrite it.
"""

from __future__ import annotations

import hashlib
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .common import canonical, digest, object_keys, read_json, write_json

BUNDLE_FILES = frozenset(
    {
        "plan.json",
        "approvals.json",
        "before.json",
        "after.json",
        "result.json",
        "assessment.json",
        "audit.jsonl",
        "report.md",
    }
)


def assessments(plan: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    grants = [op for op in result["operations"] if op["action"] == "grant"]
    departures = [op for op in result["operations"] if op["action"] == "disable_identity"]
    return [
        {
            "control_id": "IG-01",
            "title": "Identity and scope",
            "status": "model_checked",
            "evidence": ["plan.json", "before.json"],
            "finding": "Subject, policy and bounded snapshot are linked by immutable identifiers and digests.",
            "next_action": "For a pilot, validate HR authority, collection coverage and identity bindings with their owners.",
        },
        {
            "control_id": "IG-02",
            "title": "Role reconciliation",
            "status": "open"
            if not result["review"]["catalogued_assignment_target_reached"]
            else "model_checked",
            "evidence": ["before.json", "after.json", "result.json"],
            "finding": f"{len(result['review']['unexpected_assignments'])} unexpected and {len(result['review']['missing_role_assignments'])} missing assignments remain in the catalogued scope.",
            "next_action": "Resolve failed removals; collect new state and replan before requesting approvals for new grants.",
        },
        {
            "control_id": "IG-03",
            "title": "Approval before grants",
            "status": "not_applicable"
            if not grants
            else "open"
            if any(op["status"] != "simulated" for op in grants)
            else "model_checked",
            "evidence": ["approvals.json", "result.json"],
            "finding": "New grants require two distinct, plan-bound, unexpired manager and owner approvals in the model.",
            "next_action": "Replace synthetic approval assertions with authenticated, signed decisions before live execution.",
        },
        {
            "control_id": "IG-04",
            "title": "Separation of duties",
            "status": "open"
            if result["review"]["separation_of_duties_conflicts"]
            else "model_checked",
            "evidence": ["plan.json", "result.json"],
            "finding": f"{len(result['review']['separation_of_duties_conflicts'])} configured conflicts remain after simulation.",
            "next_action": "Have business owners review the conflict rules and any wider inherited access.",
        },
        {
            "control_id": "IG-05",
            "title": "Departure and expiry",
            "status": "not_applicable"
            if not departures
            else "open"
            if any(op["status"] != "simulated" for op in result["operations"])
            else "model_checked",
            "evidence": ["plan.json", "after.json", "result.json"],
            "finding": "Departure and expiry events plan IdP disablement and removal of catalogued assignments; existing sessions are not tested.",
            "next_action": "Verify actual disablement, SCIM propagation, credential handling and session expiry using each provider's supported controls.",
        },
        {
            "control_id": "IG-06",
            "title": "Review evidence",
            "status": "generated",
            "evidence": ["audit.jsonl", "manifest.json"],
            "finding": "A local hash chain and file manifest support reproducible integrity checks, not independent authenticity.",
            "next_action": "Use separated evidence writers, retention controls and a trusted signing or anchoring service in a pilot.",
        },
    ]


def _cell(value: Any) -> str:
    return (
        html.escape(str(value), quote=False)
        .replace("|", "\\|")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def render_report(
    scenario: dict[str, Any],
    plan: dict[str, Any],
    result: dict[str, Any],
    findings: list[dict[str, Any]],
) -> str:
    counts = Counter((op["action"], op["status"]) for op in result["operations"])
    lines = [
        f"# Access review: {_cell(plan['event_name'])}",
        "",
        "**Synthetic demonstration. No cloud account was changed.**",
        "",
        f"- Scenario: {_cell(scenario.get('company', {}).get('name', 'Fictional organisation'))}",
        f"- Subject: `{_cell(plan['subject_id'])}`",
        f"- Outcome: **{result['status']}**",
        f"- Plan: `{plan['plan_id']}`",
        f"- Source observation time: `{result['before']['captured_at']}` (not refreshed by simulation)",
        "- Scope: catalogued direct assignments; inherited/effective access and active sessions are outside the check.",
        "",
        "## What happened",
        "",
        f"The workflow simulated **{counts[('revoke', 'simulated')]} removals** and **{counts[('grant', 'simulated')]} grants**. "
        f"It recorded **{sum(v for (a, s), v in counts.items() if s == 'failed')} failures** and "
        f"**{sum(v for (a, s), v in counts.items() if s == 'blocked')} blocked operations**.",
        "",
        "| Provider | Action | Assignment | Result | Reason |",
        "|---|---|---|---|---|",
    ]
    for op in result["operations"]:
        label = (
            scenario["policy"]["entitlements"][op["entitlement_id"]]["label"]
            if op["entitlement_id"]
            else "Identity disabled in the local model"
        )
        lines.append(
            "| "
            + " | ".join(
                _cell(value)
                for value in (
                    op["provider"],
                    op["action"],
                    label,
                    op["status"],
                    op["result_reason"],
                )
            )
            + " |"
        )
    if not result["operations"]:
        lines.append(
            "| — | — | No changes needed in the declared scope | No-op | No duplicate assignments planned |"
        )
    lines += [
        "",
        "## Remaining work",
        "",
        f"- Unexpected assignments: {_cell(', '.join(result['review']['unexpected_assignments']) or 'none in the model')}",
        f"- Missing role assignments: {_cell(', '.join(result['review']['missing_role_assignments']) or 'none in the model')}",
        "- Live access and session revocation: **not verified**.",
        "",
        "## Control evidence",
        "",
        "`model_checked` means the local policy check succeeded. It is not a compliance opinion.",
        "",
        "| Control | Outcome | Finding | Evidence |",
        "|---|---|---|---|",
    ]
    for finding in findings:
        links = ", ".join(f"[{path}]({path})" for path in finding["evidence"])
        lines.append(
            f"| {finding['control_id']} — {finding['title']} | {finding['status']} | {_cell(finding['finding'])} | {links} |"
        )
    lines += ["", "## Reviewer actions", ""]
    lines.extend(f"- **{finding['control_id']}:** {finding['next_action']}" for finding in findings)
    lines += [
        "",
        "## Evidence limits",
        "",
        "All identities, approvals and provider outcomes are invented for this exercise. "
        "Provider exports are not collected or authenticated by this run. "
        "Checksums and the hash chain detect changes relative to the supplied bundle; "
        "someone who can rewrite the entire bundle can recompute them. "
        "Neither ISO certification nor legal compliance is established.",
        "",
    ]
    return "\n".join(lines)


def write_bundle(
    output: Path,
    scenario: dict[str, Any],
    plan: dict[str, Any],
    approvals: list[dict[str, Any]],
    result: dict[str, Any],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Evidence output directory must be empty; preserve earlier runs")
    findings = assessments(plan, result)
    for name, data in {
        "plan.json": plan,
        "approvals.json": approvals,
        "before.json": result["before"],
        "after.json": result["after"],
        "result.json": result,
        "assessment.json": findings,
    }.items():
        write_json(output / name, data)
    (output / "audit.jsonl").write_text(
        "".join(canonical(event) + "\n" for event in result["audit"]), encoding="utf-8"
    )
    (output / "report.md").write_text(
        render_report(scenario, plan, result, findings), encoding="utf-8"
    )
    manifest = {
        "schema_version": 1,
        "mode": "simulation_only",
        "plan_id": plan["plan_id"],
        "audit_head": result["audit"][-1]["hash"],
        "files": {
            name: hashlib.sha256((output / name).read_bytes()).hexdigest()
            for name in sorted(BUNDLE_FILES)
        },
        "authenticity": "Unsigned local manifest; not an independent trust anchor",
    }
    write_json(output / "manifest.json", manifest)


def verify_bundle(output: Path) -> dict[str, Any]:
    if output.is_symlink():
        raise ValueError("Evidence bundle must not be a symbolic link")
    manifest = read_json(output / "manifest.json")
    object_keys(
        manifest,
        {"schema_version", "mode", "plan_id", "audit_head", "files", "authenticity"},
        set(),
        "Manifest",
    )
    if (
        type(manifest["schema_version"]) is not int
        or manifest["schema_version"] != 1
        or manifest["mode"] != "simulation_only"
    ):
        raise ValueError("Unsupported evidence manifest")
    if not isinstance(manifest["files"], dict) or set(manifest["files"]) != BUNDLE_FILES:
        raise ValueError("Manifest must contain exactly the expected evidence files")
    if (output / "manifest.json").is_symlink():
        raise ValueError("Manifest must not be a symbolic link")
    for name, expected in manifest["files"].items():
        path = output / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or symbolic-link evidence file: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Evidence checksum mismatch: {name}")
    previous = "0" * 64
    events = []
    for index, line in enumerate(
        (output / "audit.jsonl").read_text(encoding="utf-8").splitlines(), start=1
    ):
        event = json.loads(line)
        payload = {key: value for key, value in event.items() if key != "hash"}
        if (
            event.get("sequence") != index
            or event.get("previous_hash") != previous
            or event.get("hash") != digest(payload)
        ):
            raise ValueError(f"Audit chain mismatch at event {index}")
        if event.get("plan_id") != manifest["plan_id"]:
            raise ValueError("Audit event belongs to a different plan")
        previous = event["hash"]
        events.append(event)
    if not events or previous != manifest["audit_head"]:
        raise ValueError("Audit head mismatch")
    plan = read_json(output / "plan.json")
    if (
        plan.get("plan_id") != manifest["plan_id"]
        or digest({k: v for k, v in plan.items() if k != "plan_id"}) != plan["plan_id"]
    ):
        raise ValueError("Evidence plan integrity mismatch")
    result = read_json(output / "result.json")
    if result.get("plan_id") != plan["plan_id"] or result.get("audit") != events:
        raise ValueError("Result and audit are inconsistent")
    if result.get("before") != read_json(output / "before.json") or result.get(
        "after"
    ) != read_json(output / "after.json"):
        raise ValueError("Result and snapshot files are inconsistent")
    return {
        "integrity": "verified_against_local_manifest",
        "files_checked": len(BUNDLE_FILES),
        "audit_events_checked": len(events),
        "plan_id": plan["plan_id"],
        "independent_authenticity": False,
    }
