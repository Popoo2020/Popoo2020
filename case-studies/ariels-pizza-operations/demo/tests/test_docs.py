"""Local documentation and disclosure integrity checks."""
from pathlib import Path
import re
import unittest

CASE = Path(__file__).resolve().parents[2]
DOCS = [CASE / name for name in (
    "README.md", "architecture.md", "security-and-oversight.md",
    "evidence-and-outcomes.md", "demo/README.md",
)]

class DocumentationTests(unittest.TestCase):
    def test_local_case_links_resolve(self):
        # Links outside the case directory are verified by GitHub after upload.
        for doc in DOCS:
            text = doc.read_text(encoding="utf-8")
            for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
                if target.startswith(("https:", "http:", "mailto:", "#")):
                    continue
                if target.startswith("../../"):
                    continue
                path = (doc.parent / target.split("#", 1)[0]).resolve()
                with self.subTest(document=doc.name, target=target):
                    self.assertTrue(path.exists(), f"Missing linked case file: {target}")

    def test_historical_and_new_code_separated(self):
        overview = (CASE / "README.md").read_text(encoding="utf-8")
        demo = (CASE / "demo/README.md").read_text(encoding="utf-8")
        self.assertIn("Historical", overview)
        self.assertIn("2026", overview)
        self.assertIn("NOT historical", demo)
        self.assertIn("No", demo)

    def test_evidence_does_not_claim_measured_business_improvement(self):
        evidence = (CASE / "evidence-and-outcomes.md").read_text(encoding="utf-8")
        self.assertIn("No measured baseline", evidence)
        self.assertRegex(evidence, r"not (?:historical|original)")

if __name__ == "__main__":
    unittest.main()
