# ISO42001-AI-Governance-Evidence-Toolkit

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
- and a generated readiness report.

It is designed to bridge **AI governance**, **cybersecurity GRC**, **ISO 27001 experience**, **ISO/IEC 42001 readiness**, **EU AI Act awareness**, and practical AI implementation work such as AI-assisted Shopify/e-commerce workflows.

## Repository structure

```text
data/
  ai_use_case_register.csv       # Example AI systems and organisational ownership
  ai_risk_register.csv           # Example AI risks, controls and residual risk
  control_mapping.csv            # Governance controls, owners and evidence references

docs/
  ai_policy_draft.md             # Lightweight internal AI-use policy draft
  ai_impact_assessment_example.md # Example impact assessment for an SME AI workflow

src/
  generate_readiness_report.py   # Generates a Markdown readiness summary from CSV inputs

reports/
  sample_readiness_report.md     # Example generated-style report
```

## Implemented artefacts

| Capability | Status |
|---|---|
| AI use-case register template | ✅ Implemented |
| AI risk register template | ✅ Implemented |
| AI impact assessment example | ✅ Implemented |
| AI policy draft | ✅ Implemented |
| ISO/IEC 42001-oriented control mapping | ✅ Implemented |
| Readiness report generator | ✅ Implemented |
| EU AI Act risk classification expansion | 🟡 Planned |
| Supplier due-diligence checklist | 🟡 Planned |
| Human oversight workflow examples | 🟡 Planned |
| Evidence pack export to PDF/HTML | 🟡 Planned |

## Example use cases covered

The sample register includes realistic SME scenarios such as:

- AI-assisted Shopify product descriptions and SEO content,
- AI customer-support drafting,
- HR screening support,
- internal document summarisation,
- security incident triage support.

The point is not to ban AI. The point is to make AI adoption visible, owned, risk-assessed, reviewable and evidence-backed.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
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
5. prepare a readiness report with gaps, owners and recommended next steps.

## Limitations

- This is not legal advice.
- This is not a full ISO/IEC 42001 implementation package.
- The mapping is intentionally high level and educational.
- Real organisations should adapt the artefacts to their sector, jurisdiction, risk profile, contractual obligations and professional legal/compliance guidance.

## Roadmap

1. Add supplier and model-provider due-diligence checklist.
2. Add EU AI Act-oriented risk-category notes.
3. Add a human-oversight decision log template.
4. Add AI incident and complaint handling template.
5. Add PDF export for client-facing readiness reports.
6. Add a TeenTech AI awareness-training variant for education and youth-focused contexts.
