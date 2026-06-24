# Release Checklist

Use this checklist before publishing a GitHub release such as `v0.1.0`.

## Release title

`v0.1.0 - Portfolio Readiness Release`

## Pre-release validation

- [ ] Pull request is merged into `main`.
- [ ] AI Governance Toolkit workflow passed.
- [ ] CodeQL workflow passed.
- [ ] `make validate` runs successfully.
- [ ] `reports/generated_readiness_report.md` is generated successfully.
- [ ] README links work.
- [ ] Architecture document is present.
- [ ] Threat model is present.
- [ ] Demo output document is present.
- [ ] Quality and security checklist is present.
- [ ] Changelog and version notes are present.

## Security and data review

- [ ] No real client data is included.
- [ ] No secrets, tokens or credentials are included.
- [ ] Case study is clearly labelled as simulated or anonymised.
- [ ] The project does not claim legal advice, certification or formal audit status.
- [ ] Sample data is suitable for public portfolio review.

## Suggested release description

```text
Initial portfolio readiness release of the ISO42001 AI Governance Evidence Toolkit.

This release demonstrates a practical AI governance and evidence-readiness workflow for SMEs preparing for responsible AI adoption, ISO/IEC 42001-style management-system thinking, EU AI Act readiness and cybersecurity/GRC discussions.

Included artefacts:
- AI use-case register
- AI risk register
- Governance control mapping
- Human oversight decision log
- Supplier review checklist
- AI policy and impact assessment examples
- AI incident and complaint handling template
- Sundai AI-style case study
- Readiness report generator
- Architecture documentation
- Threat model
- Demo output documentation
- Quality and security checklist
```

## Post-release actions

- [ ] Add the release link to the profile README.
- [ ] Mention the release in LinkedIn/GitHub portfolio updates.
- [ ] Consider exporting the case study to PDF for employer/client review.
