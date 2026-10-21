# Project guide for recruiters and technical reviewers

[Profile](../README.md) · [CV](ai-implementation-cv.md) · [Code and test evidence](evidence.md) · [Certifications & credentials](education-and-training.md)

My focus is AI implementation and automation: connect business systems, validate outputs and help teams use the workflow. Choose the route closest to the role.

## Review a working implementation

| Work | Where to start | Status |
|---|---|---|
| **SundAI website/API** | [Contact API](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/main/site/functions/api/contact.js) → [security tests](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/main/site/tests/contact-security.test.mjs) → [email routing tests](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/main/site/tests/contact-delivery.test.mjs) | Public JavaScript/Cloudflare implementation; 114 offline website tests passed in the dated review. |
| **Sentinel AI AutoTriage** | [Walkthrough](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/main/docs/recruiter_summary.md) → [workflow](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/main/src/auto_triage.py) → [SDK regressions](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/main/tests/test_sdk_integration.py) | Public Python prototype; 48 offline tests passed after adapter/outcome fixes. |
| **AI Governance Evidence Toolkit** | [Report generator](../ISO42001-AI-Governance-Evidence-Toolkit/src/generate_readiness_report.py) → [sample report](../ISO42001-AI-Governance-Evidence-Toolkit/reports/sample_readiness_report.md) → [tests](../ISO42001-AI-Governance-Evidence-Toolkit/tests/test_generate_readiness_report.py) | Runnable standard-library reporting tool with illustrative registers and assessments. |

Exact revisions, environments, commands and limits are in the [19 October verification record](evidence.md). Passing tests describe the tested behaviours; live deployment needs separate validation.

## Review applied workflow design

- **[Denmark in 5](../case-studies/denmark-in-5-azure/README.md):** Python/API daily-briefing workflow, editorial checks and Bicep/OIDC Azure delivery. [Engineering and CI validation](../case-studies/denmark-in-5-azure/editorial-assurance.md). Private application, public case study and sanitised release evidence.
- **[Ariel's Pizza](../case-studies/ariels-pizza-operations/README.md):** order and manager inputs translated into staff tasks, purchasing, follow-up and manager escalation across three locations. Historical builder/operator account **plus a separately authored, runnable [2026 offline Python demo](../case-studies/ariels-pizza-operations/demo/README.md)** with [unit tests](../case-studies/ariels-pizza-operations/demo/tests/test_engine.py) and [security/ownership boundaries](../case-studies/ariels-pizza-operations/security-and-oversight.md). The demo is not the original transferred tool.

## Supporting prototypes and references

| Project | Implemented scope | Limit |
|---|---|---|
| [Secure Agent Control Plane](https://github.com/Popoo2020/Secure-Agent-Control-Plane) | Validated policy loading, role-aware decisions and audit events in `src/`. | Policy-decision library; no live tool-execution broker or identity provider. |
| [RAG Security Eval Harness](https://github.com/Popoo2020/RAG-Security-Eval-Harness) | Deterministic source-risk signals, trust labels, metrics and sample reporting in `src/`. | Small authored corpus; no live model or retrieval service. |
| [DevSecOps Reference Pipeline](https://github.com/Popoo2020/DevSecOps-Reference-Pipeline) | GitHub Actions patterns for conditional Ruff, pytest, Bandit, dependency auditing, Gitleaks and CodeQL. | Reference configuration; its placeholder smoke test is not application coverage. |
| [Cloud Compliance Engine](https://github.com/Popoo2020/Cloud-Compliance-Engine-ISO27001) | Sample Azure/AWS evidence validation, freshness checks and ISO/IEC 27001-oriented reports. | Live collectors are planned. |
| [Detection Engineering Playbook](https://github.com/Popoo2020/Detection-Engineering-Playbook) | KQL/Sigma examples, ATT&CK mapping and review guidance. | Reference/lab material. |
| [LLM Security Guardrails Lab](https://github.com/Popoo2020/LLM-Security-Guardrails-Lab) | Deterministic prompt-risk checks and tests. | Lab baseline. |
| [SundAI Python ingestion baseline](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/main/src/rag_ingestion.py) | Text normalisation, overlapping chunks, deterministic IDs and metadata. | Separate from the website APIs; retrieval and a running RAG chatbot remain future work. |

Additional conceptual labs: [Entra IAM governance](../entra-iam-governance-mini-lab/README.md) · [IT/OT governance](../itot-governance-mini-lab/README.md).

For employment, I am interested in a defined implementation responsibility within a team. For consulting, a useful starting scope is one API integration, a validated AI-assisted workflow or an AI use-case and risk review. [Contact](mailto:eririmo@protonmail.com).
