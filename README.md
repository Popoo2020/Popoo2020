# Eric Ariel Rimón

**AI Implementation & Automation Specialist**

Python · API Integration · Azure Infrastructure · Security Controls

I turn business processes into practical AI workflows: connecting tools, checking outputs and helping people use the result. My work combines Python and API integration with hands-on Azure deployment, AI governance, security controls and experience leading service operations.

**My next role:** AI Implementation & Automation Specialist, including AI Adoption roles. I also welcome AI Governance / GRC Analyst roles that combine risk documentation, technical evidence and user enablement. I am happy to join as an individual contributor and take ownership of a defined piece of work.

**Availability:** from Tel Aviv in late October 2026; currently in Odense, Denmark. Open to employment and project-based work in Israel, and remote collaboration with European teams.

[Email me](mailto:eririmo@protonmail.com) · [SundAI](https://sundaibot.com/) · [Current projects](#current-projects) · [Technical portfolio](#technical-portfolio) · [Education and training](#education-and-training)

## How I can help your team

- **Implement a useful AI workflow:** map the process, connect APIs, build a Python prototype, validate outputs and document the handover.
- **Help people adopt it:** translate requirements into clear steps, prepare practical guidance and support onboarding and training.
- **Make risks visible:** document AI use cases, supplier questions, impact assessments, human oversight and supporting evidence.
- **Build checks into delivery:** use structured outputs, tests, approval gates, secret handling and CI checks appropriate to the project.

## Current projects

### Denmark in 5 — AI-assisted news briefing

I develop a Hebrew briefing workflow for Israelis living in Denmark, in collaboration with Living Denmark through SundAI. It turns Danish news and practical information into a structured daily edition.

- **My work:** source collection and enrichment, deduplication, AI-assisted selection and editing, editorial checks, and publication controls.
- **Implementation:** Python, FastAPI, Pydantic, Gemini/OpenAI integration and Telegram publishing; a Node.js bridge connects a dedicated WhatsApp Business account through WhatsApp Web. Its Azure VM and network are defined in Bicep, with GitHub OIDC authentication and separate application-secret and session-state handling.
- **Current focus:** source quality, Hebrew editorial consistency, controlled delivery and recovery when a dependency fails.

**Azure deployment evidence:** a successful VM/network deployment is recorded from September 2026. [Read the public Azure architecture case study](case-studies/denmark-in-5-azure/README.md) for the logical architecture, selected implementation patterns and evidence boundaries.

**Status:** active project; application repository private. The public case study explains the implementation without exposing credentials or recipient data.

### SundAI — practical AI adoption and governance

[SundAI](https://sundaibot.com/) is my independent initiative for AI adoption, automation, governance resources and training. It brings together the work I build and the problems I want to help teams solve.

- **My work:** a multilingual website and resource library in English, Danish and Swedish, with editable AI inventory, supplier-review and impact-assessment materials.
- **Implementation:** Cloudflare routing and JavaScript APIs, contact-form validation, rate limiting, Turnstile verification, email routing and automated checks.
- **Current focus:** making governance guidance usable, connecting it to working examples, and improving the website and enquiry workflow.

**Status:** public website and resources, with ongoing development. [Visit SundAI](https://sundaibot.com/) · [Browse resources](https://sundaibot.com/resources/) · [Review website source](https://github.com/Popoo2020/Enterprise-Sundai-Bot/tree/main/site)

## Technical portfolio

These examples show how I approach implementation, risk and verification. Each repository describes its scope and development status.

| Work to review | What I implemented |
|---|---|
| **[Denmark in 5 — Azure Delivery Architecture](case-studies/denmark-in-5-azure/README.md)** | Bicep-defined VM/network, GitHub-to-Azure OIDC, separate secrets/session handling and a controlled WhatsApp Business delivery bridge. **Historical deployment evidence reviewed; current availability requires separate verification.** |
| **[AI Governance Evidence Toolkit](https://github.com/Popoo2020/Popoo2020/tree/main/ISO42001-AI-Governance-Evidence-Toolkit)** | ISO/IEC 42001-oriented use-case and risk registers, impact assessment, supplier review, oversight templates and evidence reporting. **Portfolio toolkit with illustrative cases.** [Read the case study](https://github.com/Popoo2020/Popoo2020/blob/main/ISO42001-AI-Governance-Evidence-Toolkit/docs/executive-case-study.md). |
| **[Sentinel AI AutoTriage](https://github.com/Popoo2020/Sentinel-AI-AutoTriage)** | Incident-triage prototype with pre-model redaction, schema validation, deterministic policy checks, human approval gates and metadata-only audit events. **Controlled-demo prototype.** [Read the short walkthrough](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/main/docs/recruiter_summary.md). |
| **[Secure Agent Control Plane](https://github.com/Popoo2020/Secure-Agent-Control-Plane)** | Role-aware tool permissions, YAML policies, allow/deny/approval decisions and audit events. **Policy-engine prototype; live tool execution is a future extension.** |
| **[RAG Security Eval Harness](https://github.com/Popoo2020/RAG-Security-Eval-Harness)** | Dataset-driven checks for retrieval poisoning, indirect prompt injection and source-trust risks. **Deterministic evaluation baseline.** |

<details>
<summary><strong>More technical breadth: cloud, detection, RAG ingestion and secure delivery</strong></summary>

- **[Cloud Compliance Engine](https://github.com/Popoo2020/Cloud-Compliance-Engine-ISO27001):** validates sample Azure/AWS evidence, checks freshness and generates ISO/IEC 27001-oriented reports. Live cloud collectors are planned.
- **[DevSecOps Reference Pipeline](https://github.com/Popoo2020/DevSecOps-Reference-Pipeline):** GitHub Actions patterns for Ruff, pytest, Bandit, dependency auditing and secret scanning, with checks conditional on repository content.
- **[Detection Engineering Playbook](https://github.com/Popoo2020/Detection-Engineering-Playbook):** KQL and Sigma examples, ATT&CK mapping and rule-review guidance.
- **[LLM Security Guardrails Lab](https://github.com/Popoo2020/LLM-Security-Guardrails-Lab):** deterministic prompt-risk checks and repeatable tests.
- **[RAG Ingestion Baseline](https://github.com/Popoo2020/Enterprise-Sundai-Bot):** Python text normalisation, overlapping chunks, deterministic IDs, metadata and tests. The implemented scope is ingestion; retrieval, authentication and a running chatbot are future stages.

**Working toolkit:** Python, FastAPI, Pydantic, REST APIs, JSON/YAML, Git, GitHub Actions, pytest and JavaScript/Node.js integrations. **Applied Azure work:** Bicep, VM/VNet/NSG configuration and GitHub OIDC deployment.

**Additional foundations through training and labs:** Azure, Entra ID, IAM/RBAC, Microsoft Sentinel, KQL, Linux, Windows/Active Directory, networking, Bash, PowerShell and Terraform fundamentals.

</details>

## Experience behind the technology

- **Independent AI work — SundAI / Riimon Holdings, 2024–present:** workflow development, governance resources and technical portfolio projects, alongside business and innovation coordination.
- **Business and innovation coordination — Riimon Holdings, 2021–present:** independent advisory and Denmark–Israel relationship-building, including collaboration with Innovation Centre Denmark in Tel Aviv and coordination with university and healthcare innovation teams. This work is carried out through my own initiative.
- **Business operations and automation — Ariel's Pizza, Aug 2024–May 2025:** built and operated a concept across three sites. Developed a Python management assistant connecting Trello, Google Sheets, WhatsApp and OpenAI for operational tasks and daily staff task lists. Sold the business, concept and tool in May 2025.
- **Social services, 2017–Jan 2024; unit manager, Aug 2023–Jan 2024:** led 45+ staff, with responsibilities in onboarding, privacy procedures and regulated service operations.
- **Co-founder — Bcar.app / ChargeCast, Aug 2020–Sep 2023:** finance, product and international partner coordination for an EV charging and payments venture.

This experience helps me connect a technical solution to the people using it: clarify the need, explain decisions, organise the work and follow through.

**Languages:** native Hebrew and Swedish; fluent English and Danish; working Finnish.

## Education and training

**Academic degree:** Bachelor of Social Services (Socionom), Novia University of Applied Sciences, Finland — 2019.

**Selected completed professional training:**

- **EC-Council — CEH v13 AI, CTIA and E|CDE v2:** Certificates of Achievement for successful course completion in ethical hacking, threat intelligence and DevSecOps (2026).
- **[AI for Cybersecurity Specialization](https://coursera.org/verify/specialization/6QYARVK4C9L8)** — Johns Hopkins University / Coursera.
- **[Azure Security Engineer Professional Certificate](https://coursera.org/verify/professional-cert/FEVLO405RYWW)** — Microsoft / Coursera; AZ-500-aligned programme.
- **[AI System Impact Assessment Guidance](https://coursera.org/verify/EJRZ6JYOOE6U)** and **[ISO/IEC 22989 — Fundamentals of AI](https://coursera.org/verify/J8QCVQB3O9OK)** — BSI.
- **[Advanced Python Scripting for Cybersecurity](https://coursera.org/verify/specialization/7ZLVP69YSUSS)** — Infosec / Coursera.

<details>
<summary><strong>Additional education, completed courses and current study</strong></summary>

**Education and professional development**

- Erasmus+ Social Education exchange, Head–Heart–Hands — VIA University College, Denmark, 30 ECTS (2017).
- Pedagogical Psychology — Åbo Akademi University, Finland, 5 ECTS.
- Mini-MBA programme — International Business Management Institute (2021).

**Completed courses and programmes**

- EC-Council course-completion dates: CEH v13 AI — 14 January 2026; E|CDE v2 — 25 February 2026; CTIA — 12 March 2026.
- [AZ-104 exam-preparation specialization](https://coursera.org/verify/specialization/MOKKHGGPILO0) and [AI-900 exam-preparation specialization](https://coursera.org/verify/specialization/N7B9NHAT9ZUH) — Microsoft / Coursera.
- [Microsoft Copilot for Security](https://coursera.org/verify/MTZAM73PKYS6) — course completion.
- [Elements of AI](https://certificates.mooc.fi/validate/i38tdbu7so) — University of Helsinki and Linköping University.
- ISC2 AI for Cybersecurity — professional-development course.
- ISO/IEC 27001:2022 Lead Implementer — course completion.
- CompTIA Security+ SY0-701 Complete Course & Practice Exam — 31-hour Udemy course (2025).
- Google Automation with Python for Cybersecurity — applied coursework; Google Digital Garage — digital-business training (2018).
- Additional Azure AI, computer-vision and natural-language-processing coursework; Microsoft Sentinel/KQL labs.

**Current study:** CySA+ and AI-102 exam preparation, Terraform fundamentals and ISO/IEC 42001 AI management systems.

EC-Council entries describe course-completion certificates; Microsoft entries describe Coursera programmes and exam preparation. These labels do not claim a separate vendor certification exam pass.

</details>

## Let's work together

I am looking for a team where I can build useful AI workflows, support adoption and make the controls understandable. I am happy to start with a focused assignment: an API integration, an onboarding guide for an AI pilot, or an AI use-case and risk register. I can walk through relevant code and design decisions.

**[Contact me about a role or project](mailto:eririmo@protonmail.com)** · [SundAI](https://sundaibot.com/)
