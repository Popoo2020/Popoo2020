# ISO42001-AI-Governance-Evidence-Toolkit

[![AI Governance Toolkit](https://github.com/Popoo2020/Popoo2020/actions/workflows/ai-governance-toolkit.yml/badge.svg)](https://github.com/Popoo2020/Popoo2020/actions/workflows/ai-governance-toolkit.yml)

A practical AI governance and evidence-readiness toolkit for small and medium-sized organisations preparing for responsible AI adoption, ISO/IEC 42001-style management-system thinking, EU AI Act readiness, and cybersecurity/GRC discussions.

> **Status:** portfolio-grade governance toolkit / active expansion.  
> This is not a certification product, legal advice, or a substitute for a formal ISO/IEC 42001 audit. It is a practical evidence and documentation baseline for learning, consulting demonstrations, and SME readiness conversations.

## Why this project matters

Many SMEs are adopting tools such as ChatGPT, Microsoft Copilot, AI customer support, AI-assisted marketing, AI-enabled e-commerce workflows, and internal automation before they have clear policies, risk ownership, data boundaries, or evidence trails.

This project demonstrates how AI governance can be translated into practical artefacts:

- an AI use-case register,
- an AI risk register,
- an AI impact assessment example,
- a lightweight AI policy draft,
- an ISO/IEC 42001-oriented control/evidence mapping,
- an AI supplier due-diligence checklist,
- a human-oversight decision log,
- an AI incident and complaint handling template,
- an EU AI Act readiness classification note,
- a client-facing consulting offer,
- a client-style case study,
- and a generated readiness report.

It is designed to bridge **AI governance**, **cybersecurity GRC**, **ISO 27001 experience**, **ISO/IEC 42001 readiness**, **EU AI Act awareness**, and practical AI implementation work such as AI-assisted Shopify/e-commerce workflows.

## Repository structure

```text
data/
  ai_use_case_register.csv          # Example AI systems and organisational ownership
  ai_risk_register.csv              # Example AI risks, controls and residual risk
  control_mapping.csv               # Governance controls, owners and evidence references
  human_oversight_decision_log.csv  # Example human-review and escalation log

docs/
  executive-case-study.md                # Problem / solution / outcome summary for employers and clients
  ai_policy_draft.md                     # Lightweight internal AI-use policy draft
  ai_impact_assessment_example.md        # Example impact assessment for an SME AI workflow
  ai_supplier_due_diligence_checklist.md # Supplier/tool review checklist
  eu_ai_act_risk_classification_note.md  # Readiness note for risk-based triage
  ai_incident_response_template.md       # AI incident and complaint handling template

case_studies/
  sme_sundai_ai_governance_review.md     # Client-style Sundai AI governance review

src/
  generate_readiness_report.py      # Generates a Markdown readiness summary from CSV inputs

reports/
  sample_readiness_report.md        # Example generated-style report

consulting_offer_ai_governance_readiness.md # Client-facing service outline
```

## Implemented artefacts

| Capability | Status |
|---|---|
| Executive case study | ✅ Implemented |
| AI use-case register template | ✅ Implemented |
| AI risk register template | ✅ Implemented |
| AI impact assessment example | ✅ Implemented |
| AI policy draft | ✅ Implemented |
| ISO/IEC 42001-oriented control mapping | ✅ Implemented |
| AI supplier due-diligence checklist | ✅ Implemented |
| EU AI Act risk-classification readiness note | ✅ Implemented |
| Human oversight decision log | ✅ Implemented |
| AI incident and complaint handling template | ✅ Implemented |
| Client-facing AI governance consulting offer | ✅ Implemented |
| Sundai AI client-style governance case study | ✅ Implemented |
| Readiness report generator | ✅ Implemented |
| CI validation for report generation | ✅ Implemented |
| Evidence pack export to PDF/HTML | 🟡 Planned |
| TeenTech AI awareness-training variant | 🟡 Planned |

## Example use cases covered

The sample register includes realistic SME scenarios such as:

- AI-assisted Shopify product descriptions and SEO content,
- AI customer-support drafting,
- recruitment note assistance,
- internal document summarisation,
- security workflow summarisation,
- Sundai AI-style workflow adoption review.

The point is not to ban AI. The point is to make AI adoption visible, owned, risk-assessed, reviewable and evidence-backed.

## Quickstart

From the repository root:

```bash
cd ISO42001-AI-Governance-Evidence-Toolkit
python -m venv .venv
source .venv/bin/activate
python src/generate_readiness_report.py
```

Windows PowerShell activation example:

```powershell
cd ISO42001-AI-Governance-Evidence-Toolkit
python -m venv .venv
.venv\Scripts\Activate.ps1
python src/generate_readiness_report.py
```

The script reads CSV files from `data/` and writes:

```text
reports/generated_readiness_report.md
```

## Portfolio value

This project demonstrates practical ability to turn AI governance concepts into business-ready documentation:

- AI system inventory thinking,
- AI risk and impact assessment,
- evidence-based governance,
- policy drafting,
- control ownership,
- supplier/tool review,
- human oversight and escalation,
- incident/complaint handling,
- client-style analysis,
- SME consulting packaging,
- and a bridge between cybersecurity compliance and applied AI implementation.

It is especially relevant for roles and freelance services such as:

- AI Governance Consultant,
- Cybersecurity GRC Consultant,
- ISO 42001 Readiness Advisor,
- EU AI Act Readiness Support,
- Responsible AI Implementation Consultant,
- AI & Cyber Awareness Trainer.

## Suggested consulting package

**AI Governance Readiness Assessment for SMEs**

A lightweight engagement could include:

1. identify and document current AI use cases,
2. classify data and affected stakeholders,
3. map risks and existing safeguards,
4. create an AI-use policy draft,
5. review AI suppliers/tools,
6. define human oversight and incident escalation expectations,
7. prepare a readiness report with gaps, owners and recommended next steps.

See `consulting_offer_ai_governance_readiness.md` for a client-facing service outline.

## Case study

- [`docs/executive-case-study.md`](docs/executive-case-study.md) — concise problem / solution / outcome summary for employers, recruiters and potential consulting clients.
- [`case_studies/sme_sundai_ai_governance_review.md`](case_studies/sme_sundai_ai_governance_review.md) — anonymised/simulated client-style review showing how the toolkit can be applied to a company using Sundai AI-style workflows.

## Limitations

- This is not legal advice.
- This is not a full ISO/IEC 42001 implementation package.
- This is not a formal EU AI Act legal-classification tool.
- The case study is a portfolio demonstration, not a claim of a real paid client engagement.
- The mapping is intentionally high level and educational.
- Real organisations should adapt the artefacts to their sector, jurisdiction, risk profile, contractual obligations and professional legal/compliance guidance.

## Roadmap

1. Add PDF/HTML export for client-facing readiness reports.
2. Add richer evidence-reference schema and owner sign-off fields.
3. Add a TeenTech AI awareness-training variant for education and youth-focused contexts.
4. Add a management workshop deck outline.
5. Add optional questionnaire-based scoring for readiness maturity.
