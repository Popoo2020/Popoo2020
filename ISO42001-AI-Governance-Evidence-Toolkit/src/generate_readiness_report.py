"""Generate a lightweight AI governance readiness report from CSV evidence.

This script is intentionally dependency-free and portfolio-friendly. It reads
sample governance artefacts from the data directory and writes a Markdown report
that can be adapted for SME consulting conversations.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
REPORTS_DIR = REPO_ROOT / "reports"


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of dictionaries."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def count_by(rows: list[dict[str, str]], field: str) -> Counter[str]:
    """Count rows by a named field, normalising empty values."""
    return Counter((row.get(field) or "Unknown").strip() or "Unknown" for row in rows)


def render_counter(counter: Counter[str]) -> str:
    """Render a Counter as Markdown bullets."""
    if not counter:
        return "- No data available"
    return "\n".join(f"- {key}: **{value}**" for key, value in sorted(counter.items()))


def build_report() -> str:
    """Build a Markdown readiness report from the sample CSV artefacts."""
    use_cases = read_csv(DATA_DIR / "ai_use_case_register.csv")
    risks = read_csv(DATA_DIR / "ai_risk_register.csv")
    controls = read_csv(DATA_DIR / "control_mapping.csv")

    risk_levels = count_by(use_cases, "risk_level")
    use_case_status = count_by(use_cases, "status")
    residual_risks = count_by(risks, "residual_risk")
    control_status = count_by(controls, "status")

    high_risk_use_cases = [
        row for row in use_cases if row.get("risk_level", "").strip().lower() == "high"
    ]
    open_controls = [
        row for row in controls if row.get("status", "").strip().lower() != "implemented"
    ]

    lines = [
        "# AI Governance Readiness Report",
        "",
        "> Generated from sample AI governance artefacts. This is a portfolio/readiness example, not legal advice or certification evidence.",
        "",
        "## Executive summary",
        "",
        f"- AI use cases reviewed: **{len(use_cases)}**",
        f"- Risks recorded: **{len(risks)}**",
        f"- Governance controls mapped: **{len(controls)}**",
        f"- High-risk use cases requiring stronger oversight: **{len(high_risk_use_cases)}**",
        f"- Controls not fully implemented: **{len(open_controls)}**",
        "",
        "## Use-case risk levels",
        "",
        render_counter(risk_levels),
        "",
        "## Use-case lifecycle status",
        "",
        render_counter(use_case_status),
        "",
        "## Residual risk overview",
        "",
        render_counter(residual_risks),
        "",
        "## Governance-control implementation status",
        "",
        render_counter(control_status),
        "",
        "## High-risk use cases",
        "",
    ]

    if high_risk_use_cases:
        lines.extend([
            "| Use case | Owner | Human oversight | Evidence reference |",
            "|---|---|---|---|",
        ])
        for row in high_risk_use_cases:
            lines.append(
                f"| {row['name']} | {row['owner']} | {row['human_oversight']} | {row['evidence_ref']} |"
            )
    else:
        lines.append("No high-risk use cases identified in the current register.")

    lines.extend([
        "",
        "## Controls requiring follow-up",
        "",
    ])

    if open_controls:
        lines.extend([
            "| Control | Area | Owner | Status | Evidence example |",
            "|---|---|---|---|---|",
        ])
        for row in open_controls:
            lines.append(
                f"| {row['control_id']} | {row['control_area']} | {row['owner']} | {row['status']} | {row['evidence_example']} |"
            )
    else:
        lines.append("All mapped controls are marked implemented in the current sample dataset.")

    lines.extend([
        "",
        "## Recommended next steps",
        "",
        "1. Confirm ownership for every AI use case.",
        "2. Review high-risk use cases before deployment or expansion.",
        "3. Add supplier/tool approval evidence for AI platforms.",
        "4. Formalise human-review requirements for customer-facing or decision-support outputs.",
        "5. Repeat the readiness review periodically and after material workflow changes.",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    """Generate the readiness report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORTS_DIR / "generated_readiness_report.md"
    output_path.write_text(build_report(), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
