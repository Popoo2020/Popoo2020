# Project guide for recruiters and technical reviewers

[Profile](../README.md) · [AI implementation CV](ai-implementation-cv.md) · [Code & validation evidence](evidence.md) · [Education & training](education-and-training.md)

My focus is identity and cloud security automation, with related work in AI-assisted workflows and business-system integration. Choose the review route closest to your role; each entry distinguishes implementation, demonstration and design work.

## Choose a review route

| Role or responsibility | Start here | What to inspect |
|---|---|---|
| Identity / IAM and access governance | [Multi-Cloud Identity Governance](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance) | A role change, manager/owner approvals, a failed removal and the resulting evidence. |
| Security automation | [Sentinel AI AutoTriage](https://github.com/Popoo2020/Sentinel-AI-AutoTriage) | Policy checks around AI recommendations, redaction, blocked actions and adapter tests. |
| AI / API implementation | [SundAI APIs](https://github.com/Popoo2020/Enterprise-Sundai-Bot/tree/main/site) and [Denmark in 5](../case-studies/denmark-in-5-azure/README.md) | Input validation, integration boundaries, failure handling and Azure delivery patterns. |
| Governance and control evidence | [Identity control mapping](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance/blob/main/docs/control-mapping.md) and [AI Governance Evidence Toolkit](../ISO42001-AI-Governance-Evidence-Toolkit/README.md) | How an operational requirement becomes a control, a finding and a reviewable record. |

## Identity and security automation

### Multi-Cloud Identity Governance

Workforce changes connect to Azure/Entra, AWS and GCP export validation, a role policy, manager and resource-owner approvals, and review evidence. In the failure example, an unsuccessful removal blocks all new grants.

[Project](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance) · [Successful move](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance/blob/main/examples/output/mover/report.md) · [Failure case](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance/blob/main/examples/output/failed-removal/report.md) · [Five-minute walkthrough](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance/blob/main/docs/interview-guide.md)

**Status:** runnable local implementation; 87 tests passed in the 26 November 2026 review. Inputs and approvals are synthetic; cloud execution and sessions are not validated. [Validation record](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance/blob/main/docs/validation.md). The [original profile-repository copy](../projects/multi-cloud-identity-governance/README.md) remains available for existing links.

### Sentinel AI AutoTriage

Python incident workflow with structured recommendations, deterministic decision gates, redaction and audit events.

[Walkthrough](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/main/docs/recruiter_summary.md) · [Workflow code](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/main/src/auto_triage.py) · [SDK adapter tests](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/main/tests/test_sdk_integration.py)

**Status:** controlled-demo prototype; 48 offline tests passed in the 19 October 2026 review. Live tenant operations and model quality were not validated in that review.

## Applied AI and API workflows

| Project | What it demonstrates | Status and evidence |
|---|---|---|
| [SundAI website & APIs](https://github.com/Popoo2020/Enterprise-Sundai-Bot/tree/main/site) | JavaScript/Cloudflare enquiry validation, routing and failure handling. | Public implementation; 114 offline tests passed in the 19 October 2026 review. [API code](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/main/site/functions/api/contact.js) · [Tests](https://github.com/Popoo2020/Enterprise-Sundai-Bot/tree/main/site/tests). |
| [Denmark in 5](../case-studies/denmark-in-5-azure/README.md) | Source processing, editorial checks and Azure delivery with Bicep and OIDC. | Private application with a public case study and sanitised evidence. The October review recorded 875 Python tests and 23 overlapping editorial cases. [Validation](../case-studies/denmark-in-5-azure/editorial-assurance.md). |
| [Shopify launch workflow](../case-studies/shopify-launch-workflow/README.md) | Budget/margin gates, supplier fulfilment and a signed order rehearsal. | Public case study and code; inspect the [security/privacy design](../case-studies/shopify-launch-workflow/docs/security-privacy-ai.md) and [tests](../case-studies/shopify-launch-workflow/tests) for scope. |
| [Ariel's Pizza operations automation](../case-studies/ariels-pizza-operations/README.md) | Ordering, staff tasks, purchasing and manager escalation in a three-location business. | Historical builder/operator account; original source private/transferred. A separate synthetic [2026 Python demo](../case-studies/ariels-pizza-operations/demo/README.md) passed 33 offline tests on 21 October 2026. |

The [SundAI Python ingestion baseline](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/main/src/rag_ingestion.py) is a component of the SundAI repository, separate from the website APIs. It covers normalisation, chunking, deterministic IDs and metadata; a running RAG service remains future work.

## Governance, prototypes and reference work

| Project | Implemented scope | Boundary |
|---|---|---|
| [AI Governance Evidence Toolkit](../ISO42001-AI-Governance-Evidence-Toolkit/README.md) | AI inventories, supplier reviews, impact assessments and a Python report generator. | Illustrative resources and local tests; no organisational certification claim. |
| [Secure Agent Control Plane](https://github.com/Popoo2020/Secure-Agent-Control-Plane) | Policy loading, role-aware tool decisions and audit events. | Policy-decision library; no live tool-execution broker or identity provider. |
| [RAG Security Eval Harness](https://github.com/Popoo2020/RAG-Security-Eval-Harness) | Source-risk signals, trust labels, metrics and sample reports. | Small authored corpus; no live model or retrieval service. |
| [DevSecOps Reference Pipeline](https://github.com/Popoo2020/DevSecOps-Reference-Pipeline) | GitHub Actions patterns for quality, dependency and secret checks. | Reference configuration; a placeholder smoke test is not application coverage. |
| [Cloud Compliance Engine](https://github.com/Popoo2020/Cloud-Compliance-Engine-ISO27001) | Sample Azure/AWS evidence validation, freshness checks and ISO 27001-oriented reports. | Live collectors are planned. |
| [Detection Engineering Playbook](https://github.com/Popoo2020/Detection-Engineering-Playbook) | KQL/Sigma examples, ATT&CK mapping and review guidance. | Reference/lab material. |
| [LLM Security Guardrails Lab](https://github.com/Popoo2020/LLM-Security-Guardrails-Lab) | Deterministic prompt-risk checks and tests. | Lab baseline. |
| [Entra IAM governance mini-lab](../entra-iam-governance-mini-lab/README.md) | Identity-governance design and review concepts. | Conceptual lab; the multi-cloud project provides the runnable extension. |
| [IT/OT governance mini-lab](../itot-governance-mini-lab/README.md) | Ownership, policy and review concepts for IT/OT. | Conceptual lab. |

## Working together

My business and team-management background informs requirements, priorities, ownership and handover. For employment, I am interested in a defined implementation responsibility within a team. A consulting engagement can start with one scoped access workflow, API integration or evidence-reporting task.

[Discuss a role or project](mailto:eririmo@protonmail.com) · [Check revisions, commands and validation limits](evidence.md)
