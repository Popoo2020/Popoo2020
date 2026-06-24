from pathlib import Path
import tempfile
import unittest

from src import generate_readiness_report as report


class TestGenerateReadinessReport(unittest.TestCase):
    def test_build_report_contains_expected_sections(self) -> None:
        output = report.build_report()

        self.assertIn("AI Governance Readiness Report", output)
        self.assertIn("High-risk use cases", output)
        self.assertIn("Controls requiring follow-up", output)
        self.assertIn("Recommended next steps", output)

    def test_read_csv_validates_required_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample.csv"
            path.write_text("name,status\nExample,Implemented\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                report.read_csv(path, {"name", "missing_column"})

    def test_markdown_escape_handles_table_separator(self) -> None:
        self.assertEqual(report.escape_md("A | B"), "A \\| B")

    def test_count_by_normalises_empty_values(self) -> None:
        rows = [{"status": ""}, {"status": "Ready"}, {}]
        counts = report.count_by(rows, "status")

        self.assertEqual(counts["Unknown"], 2)
        self.assertEqual(counts["Ready"], 1)


if __name__ == "__main__":
    unittest.main()
