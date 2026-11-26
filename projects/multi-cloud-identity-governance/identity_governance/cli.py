"""Command-line interface. No command makes cloud API requests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .common import read_json, write_json
from .engine import demo_approvals, make_plan, simulate
from .evidence import verify_bundle, write_bundle
from .providers import normalize_aws, normalize_azure, normalize_gcp

DEFAULT_SCENARIO = "examples/scenario.json"


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Plan, simulate and review identity access changes. No cloud writes."
    )
    commands = root.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Run synthetic success and failure scenarios")
    demo.add_argument("--scenario", default=DEFAULT_SCENARIO)
    demo.add_argument("--output", type=Path, default=Path("build/demo"))
    plan = commands.add_parser("plan", help="Produce a reviewable plan without executing it")
    plan.add_argument("--scenario", default=DEFAULT_SCENARIO)
    plan.add_argument("--event", default="mover")
    plan.add_argument(
        "--snapshot", help="Use an explicitly imported or previously simulated snapshot"
    )
    plan.add_argument("--output", type=Path, required=True)
    run = commands.add_parser(
        "simulate", help="Evaluate an existing plan against supplied synthetic approvals"
    )
    run.add_argument("--scenario", default=DEFAULT_SCENARIO)
    run.add_argument("--plan", required=True)
    run.add_argument("--approvals", required=True)
    run.add_argument("--snapshot")
    run.add_argument("--output", type=Path, required=True)
    normalize = commands.add_parser("normalize", help="Normalize one bounded provider export")
    normalize.add_argument("--provider", choices=["azure", "aws", "gcp"], required=True)
    normalize.add_argument("--input", required=True)
    normalize.add_argument("--output", type=Path, required=True)
    importer = commands.add_parser(
        "import-snapshot",
        help="Map a complete declared export scope into the entitlement catalogue",
    )
    importer.add_argument("--scenario", default=DEFAULT_SCENARIO)
    importer.add_argument("--subject", required=True)
    importer.add_argument("--input", required=True)
    importer.add_argument("--captured-at", required=True)
    importer.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser(
        "verify", help="Verify evidence relative to its unsigned local manifest"
    )
    verify.add_argument("--bundle", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "demo":
            scenario = read_json(args.scenario)
            if args.output.exists() and any(args.output.iterdir()):
                raise ValueError(
                    "Demo output directory must be empty; choose a new path to preserve evidence"
                )
            cases = [
                ("mover", "mover"),
                ("failed-removal", "mover"),
                ("unapproved", "mover"),
                ("joiner", "joiner"),
                ("leaver", "leaver"),
                ("contractor-expiry", "contractor-expiry"),
                ("access-review", "access-review"),
            ]
            summaries = []
            for name, event in cases:
                plan = make_plan(scenario, event)
                approvals = [] if name == "unapproved" else demo_approvals(plan)
                failures = (
                    {
                        op["operation_id"]
                        for op in plan["operations"]
                        if op["provider"] == "aws" and op["action"] == "revoke"
                    }
                    if name == "failed-removal"
                    else set()
                )
                result = simulate(scenario, plan, approvals, fail_operations=failures)
                output = args.output / name
                write_bundle(output, scenario, plan, approvals, result)
                verify_bundle(output)
                summaries.append(
                    {"case": name, "status": result["status"], "report": str(output / "report.md")}
                )
            write_json(args.output / "summary.json", summaries)
            print("Synthetic demonstration: no cloud account changed.")
            for item in summaries:
                print(f"{item['case']}: {item['status']} -> {item['report']}")
        elif args.command == "plan":
            snapshot = read_json(args.snapshot) if args.snapshot else None
            plan = make_plan(read_json(args.scenario), args.event, snapshot)
            write_json(args.output, plan)
            print(
                f"Plan {plan['plan_id']}: {len(plan['operations'])} proposed operations -> {args.output}"
            )
        elif args.command == "simulate":
            scenario = read_json(args.scenario)
            plan, approvals = read_json(args.plan), read_json(args.approvals)
            snapshot = read_json(args.snapshot) if args.snapshot else None
            result = simulate(scenario, plan, approvals, snapshot=snapshot)
            write_bundle(args.output, scenario, plan, approvals, result)
            print(f"{result['status']} -> {args.output / 'report.md'}")
        elif args.command == "normalize":
            normalizer = {"azure": normalize_azure, "aws": normalize_aws, "gcp": normalize_gcp}[
                args.provider
            ]
            records = normalizer(read_json(args.input))
            write_json(args.output, records)
            print(f"{len(records)} supported direct assignments -> {args.output}")
        elif args.command == "import-snapshot":
            from .imports import snapshot_from_exports

            if args.output.exists() and any(args.output.iterdir()):
                raise ValueError("Import output directory must be empty")
            imported = snapshot_from_exports(
                read_json(args.scenario), args.subject, read_json(args.input), args.captured_at
            )
            write_json(args.output / "snapshot.json", imported["snapshot"])
            write_json(args.output / "provenance.json", imported["evidence"])
            print(f"Bounded snapshot and provenance -> {args.output}")
        elif args.command == "verify":
            print(json.dumps(verify_bundle(args.bundle), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Cannot complete request: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
