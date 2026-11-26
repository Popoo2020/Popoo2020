"""Evidence integrity and end-to-end command-line acceptance checks."""

import hashlib
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from identity_governance.cli import main
from identity_governance.common import read_json, write_json
from identity_governance.engine import demo_approvals, make_plan, simulate
from identity_governance.evidence import verify_bundle, write_bundle

ROOT = Path(__file__).resolve().parents[1]


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name) / "bundle"
        self.scenario = read_json(ROOT / "examples/scenario.json")
        self.plan = make_plan(self.scenario, "mover")
        self.approvals = demo_approvals(self.plan)
        self.result = simulate(self.scenario, self.plan, self.approvals)
        write_bundle(self.output, self.scenario, self.plan, self.approvals, self.result)

    def test_bundle_checksums_and_chain_verify_without_claiming_authenticity(self):
        report = verify_bundle(self.output)
        self.assertEqual(report["files_checked"], 8)
        self.assertEqual(report["audit_events_checked"], 8)
        self.assertFalse(report["independent_authenticity"])

    def test_changed_report_is_detected(self):
        (self.output / "report.md").write_text("All real cloud access was revoked.\n")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            verify_bundle(self.output)

    def test_changed_audit_chain_is_detected_even_if_its_file_hash_is_updated(self):
        path = self.output / "audit.jsonl"
        events = [json.loads(line) for line in path.read_text().splitlines()]
        events[1]["details"]["status"] = "failed"
        path.write_text("".join(json.dumps(event) + "\n" for event in events))
        manifest = read_json(self.output / "manifest.json")
        manifest["files"]["audit.jsonl"] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json(self.output / "manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "Audit chain mismatch"):
            verify_bundle(self.output)

    def test_manifest_cannot_reference_files_outside_the_bundle(self):
        manifest = read_json(self.output / "manifest.json")
        manifest["files"]["../private.txt"] = "0" * 64
        write_json(self.output / "manifest.json", manifest)
        with self.assertRaises(ValueError):
            verify_bundle(self.output)

    def test_symbolic_link_evidence_is_rejected(self):
        path = self.output / "report.md"
        saved = path.read_bytes()
        path.unlink()
        replacement = Path(self.temporary.name) / "other-report.md"
        replacement.write_bytes(saved)
        path.symlink_to(replacement)
        with self.assertRaises(ValueError):
            verify_bundle(self.output)

    def test_same_inputs_produce_the_same_evidence_bytes(self):
        second = Path(self.temporary.name) / "repeat"
        write_bundle(second, self.scenario, self.plan, self.approvals, self.result)
        self.assertEqual(
            {p.name: p.read_bytes() for p in self.output.iterdir()},
            {p.name: p.read_bytes() for p in second.iterdir()},
        )

    def test_existing_evidence_is_not_silently_overwritten(self):
        before = (self.output / "manifest.json").read_bytes()
        with self.assertRaises(ValueError):
            write_bundle(self.output, self.scenario, self.plan, self.approvals, self.result)
        self.assertEqual(before, (self.output / "manifest.json").read_bytes())

    def test_report_escapes_untrusted_labels(self):
        self.scenario["policy"]["entitlements"]["azure.finance"]["label"] = (
            "<script>alert(1)</script>|Other column"
        )
        output = Path(self.temporary.name) / "escaped"
        write_bundle(output, self.scenario, self.plan, self.approvals, self.result)
        report = (output / "report.md").read_text()
        self.assertNotIn("<script>", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertIn("\\|Other column", report)

    def test_cli_runs_all_scenarios_and_verifies_evidence(self):
        output = Path(self.temporary.name) / "demo"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                main(
                    [
                        "demo",
                        "--scenario",
                        str(ROOT / "examples/scenario.json"),
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            self.assertEqual(main(["verify", "--bundle", str(output / "failed-removal")]), 0)
        summary = read_json(output / "summary.json")
        self.assertEqual(len(summary), 7)
        self.assertEqual(
            next(item["status"] for item in summary if item["case"] == "failed-removal"),
            "partial_simulation",
        )

    def test_cli_imports_provider_exports_then_plans_mover(self):
        output = Path(self.temporary.name) / "imported"
        plan = Path(self.temporary.name) / "imported-plan.json"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                main(
                    [
                        "import-snapshot",
                        "--scenario",
                        str(ROOT / "examples/scenario.json"),
                        "--subject",
                        "emp-014",
                        "--input",
                        str(ROOT / "examples/export-bundle.json"),
                        "--captured-at",
                        "2026-11-26T08:55:00Z",
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "plan",
                        "--scenario",
                        str(ROOT / "examples/scenario.json"),
                        "--snapshot",
                        str(output / "snapshot.json"),
                        "--output",
                        str(plan),
                    ]
                ),
                0,
            )
        imported = read_json(plan)
        self.assertEqual(len(imported["operations"]), 6)
        self.assertFalse(read_json(output / "provenance.json")["source_authenticated"])

    def test_cli_reports_invalid_input_as_failure(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(
                main(
                    [
                        "plan",
                        "--scenario",
                        str(ROOT / "examples/scenario.json"),
                        "--event",
                        "unknown",
                        "--output",
                        str(Path(self.temporary.name) / "invalid.json"),
                    ]
                ),
                2,
            )


if __name__ == "__main__":
    unittest.main()
