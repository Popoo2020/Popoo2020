# Eric Ariel Rimón

**AI Implementation, Automation & Security**

Python · REST APIs · Azure · FastAPI · Pydantic · GitHub Actions · AI governance

I build AI-assisted workflows that connect business systems, validate model outputs and turn information into useful actions. My work combines Python/API development, cloud delivery, security controls and practical adoption.

[Technical evidence & test results](career-portfolio/evidence.md) · [Project guide](career-portfolio/README.md) · [Certifications & credentials](career-portfolio/education-and-training.md) · [SundAI](https://sundaibot.com/) · [Contact](mailto:eririmo@protonmail.com)

## Start with the implementation

| Project | Technical focus | Code and evidence |
|---|---|---|
| **Sentinel AI AutoTriage** | Python incident workflow, Azure SDK integration, structured recommendations, deterministic decision gates, redaction and audit events. | [Source](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/tree/main/src) · [Tests](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/tree/main/tests) · [CI](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/runs/39241641427). Controlled-demo prototype; **48 tests passed**. |
| **SundAI website & APIs** | JavaScript/Cloudflare APIs, input and origin validation, Turnstile checks, email routing, escaped HTML and retry handling. | [API implementation](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/main/site/functions/api/contact.js) · [Tests](https://github.com/Popoo2020/Enterprise-Sundai-Bot/tree/main/site/tests). **114 offline JavaScript tests passed**. |
| **Denmark in 5** | Python/FastAPI information pipeline, source processing, deduplication, AI-assisted editing, publication checks and Azure/Bicep deployment with OIDC. | [Architecture](case-studies/denmark-in-5-azure/README.md) · [Implementation patterns](case-studies/denmark-in-5-azure/implementation-excerpts.md) · [CI validation](case-studies/denmark-in-5-azure/editorial-assurance.md). Private application; public case study. **875 Python tests passed**. |
| **AI Governance Evidence Toolkit** | AI inventories, supplier reviews, impact assessments and a Python report generator with validation tests. | [Toolkit](ISO42001-AI-Governance-Evidence-Toolkit/README.md) · [Source](ISO42001-AI-Governance-Evidence-Toolkit/src/generate_readiness_report.py) · [Tests](ISO42001-AI-Governance-Evidence-Toolkit/tests/test_generate_readiness_report.py). Illustrative governance resources; **4 tests passed**. |
| **Ariel's Pizza — AI Operations Automation** | Historical three-location business assistant: ordering, task coordination and manager escalation. Independent 2026 Python demo illustrates validated decisions, human oversight and audit boundaries. | [Case study](case-studies/ariels-pizza-operations/README.md) · [Architecture](case-studies/ariels-pizza-operations/architecture.md) · [Demo code](case-studies/ariels-pizza-operations/demo/engine.py) · [Tests](case-studies/ariels-pizza-operations/demo/tests/test_engine.py). Original implementation private/transferred; demo is synthetic. **33 offline tests passed** in [GitHub CI](https://github.com/Popoo2020/Popoo2020/actions/runs/39579721199). |

Other project test results are from the **19 October 2026 review**; the separate Ariel's Pizza demonstration passed its own CI on **21 October 2026**. These use offline fixtures and mocked or disabled external services. Exact revisions, commands and validation scope are in the [evidence guide](career-portfolio/evidence.md). Denmark in 5 also passed 23 editorial acceptance cases that overlap its regression suite.

## What I implement

- **API and workflow integration:** Python, REST, FastAPI, Pydantic, JSON/YAML, OpenAI/Gemini and JavaScript/Node.js; structured inputs, outputs and explicit failure handling.
- **Cloud delivery:** Azure infrastructure with Bicep, GitHub Actions and OIDC; separate credential handling, bounded retries, runtime limits and delivery-state tracking.
- **AI security controls:** model-output validation, deterministic policy checks, redaction, human approval and audit events.
- **Engineering quality:** pytest, regression cases, SDK contract checks, Ruff, Bandit and dependency auditing, with reproducible commands and documented operating limits.
- **Implementation and adoption:** requirements, acceptance criteria, workflow design, technical documentation and practical handover.

## Applied operations

For **Ariel's Pizza**, I built a Python/OpenAI operations assistant connecting Wolt and ordering APIs with Trello, Google Sheets and WhatsApp across three locations. It supported stock checks, purchasing lists, customer follow-up and shift-cover coordination, with manager escalation for uncertain or critical decisions. [Historical workflow case](case-studies/ariels-pizza-operations/README.md) · [Separate runnable 2026 offline demo](case-studies/ariels-pizza-operations/demo/README.md). The original source and records remain private/transferred; the demonstration uses invented inputs and no live integrations.

## More public code

- [Secure Agent Control Plane](https://github.com/Popoo2020/Secure-Agent-Control-Plane) — role-aware policy decisions and audit events.
- [RAG Security Eval Harness](https://github.com/Popoo2020/RAG-Security-Eval-Harness) — deterministic source-risk evaluation, trust labels and test metrics.
- [DevSecOps Reference Pipeline](https://github.com/Popoo2020/DevSecOps-Reference-Pipeline) — reusable GitHub Actions patterns for code, dependency and secret checks.

## Certifications & credentials

Selected credentials cover **Azure security, AI for cybersecurity, Python security automation, ethical hacking, threat intelligence, DevSecOps and AI impact assessment**.

[View credential titles, issuers and verification links](career-portfolio/education-and-training.md).

I can walk through the code, architecture, tests and deployment decisions behind these projects. **[Discuss an implementation or automation project](mailto:eririmo@protonmail.com).**
