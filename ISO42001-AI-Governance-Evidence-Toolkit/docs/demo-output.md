# Demo Output

This file documents the expected command-line and report output for portfolio review.

## Generate the readiness report

```bash
cd ISO42001-AI-Governance-Evidence-Toolkit
python src/generate_readiness_report.py
```

Expected console output:

```text
Wrote /path/to/ISO42001-AI-Governance-Evidence-Toolkit/reports/generated_readiness_report.md
```

## Expected report sections

The generated report should include:

```text
# AI Governance Readiness Report
## Executive summary
## Use-case risk levels
## Use-case lifecycle status
## Residual risk overview
## Governance-control implementation status
## High-risk use cases
## Controls requiring follow-up
## Recommended next steps
```

## Example management snapshot

```text
AI use cases reviewed: 5
Risks recorded: 6
Governance controls mapped: 8
High-risk use cases requiring stronger oversight: 2
Controls not fully implemented: 4
```

## Quality checks

The CI workflow validates that:

- unit tests pass,
- the readiness report can be generated,
- the generated report contains the expected core headings.
