# Eric Ariel Rimón

## Identity & Cloud Security Automation

I build Python tools for access changes, approval checks and security workflows. My focus is making each decision easy to inspect: what should change, who approved it and what happens when a step fails.

I bring **10+ years across business operations, entrepreneurship and team management**. That background shapes how I approach technical work: understand the process, agree on priorities with the team and leave a result someone else can maintain.

**Interested in IAM, security automation and technical implementation roles within a team.** I also take on defined automation projects through [SundAI](https://sundaibot.com/).

[Project guide](career-portfolio/README.md) · [Code & validation evidence](career-portfolio/evidence.md) · [Education & training](career-portfolio/education-and-training.md) · [Contact](mailto:eririmo@protonmail.com)

## Three projects to start with

### 1. Multi-Cloud Identity Governance

**A role change should remove old access and make new access reviewable.**

An employee moves from operations to finance. This Python workflow maps Entra ID, AWS IAM Identity Center and Google Cloud IAM exports to an access plan, checks manager and resource-owner approvals, and records the outcome. If a removal fails, new grants stop.

**Scope:** runnable local implementation with synthetic data; cloud changes are simulated.

[Run the project](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance) · [See the failure case](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance/blob/main/examples/output/failed-removal/report.md) · [Five-minute walkthrough](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance/blob/main/docs/interview-guide.md) · [Tests & CI](https://github.com/Popoo2020/Multi-Cloud-Identity-Governance/actions/workflows/ci.yml)

### 2. Sentinel AI AutoTriage

**An AI recommendation needs clear rules before it can trigger an action.**

A Python incident-triage workflow with structured recommendations, deterministic policy checks, redaction and audit events. Its tests cover permitted and blocked actions, Azure SDK adapters and failed writes.

**Scope:** controlled-demo prototype; external services were mocked in the documented validation.

[Project](https://github.com/Popoo2020/Sentinel-AI-AutoTriage) · [Workflow code](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/main/src/auto_triage.py) · [Tests](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/tree/main/tests) · [Validation record](career-portfolio/evidence.md#sentinel-ai-autotriage)

### 3. SundAI Website & APIs

**An enquiry should be validated, routed and given a clear outcome.**

Public JavaScript/Cloudflare API implementation with input and origin validation, Turnstile checks, email routing, escaped HTML and explicit delivery-failure handling.

**Scope:** public website/API code; validation uses offline tests with mocked providers.

[API code](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/main/site/functions/api/contact.js) · [Tests](https://github.com/Popoo2020/Enterprise-Sundai-Bot/tree/main/site/tests) · [Website](https://sundaibot.com/) · [Dated evidence](career-portfolio/evidence.md#sundai-website-and-enquiry-api)

## How I approach the work

- **Start with the process:** agree on the need, the owner and the acceptance criteria with the manager and team.
- **Make controls explicit:** map access, validate inputs and define where approval or escalation is needed.
- **Make failure visible:** test blocked actions and partial outcomes, then document what needs attention.
- **Make handover practical:** explain the decisions, operating limits and next steps in language the team can use.

**Tools used in these projects:** Python · REST APIs · Microsoft Entra / Azure · JavaScript · GitHub Actions. The wider portfolio also includes FastAPI, Pydantic, Bicep and OIDC delivery patterns.

## More of the portfolio

The [full project guide](career-portfolio/README.md) groups the work by identity and access, security automation, AI implementation and governance evidence. It includes the Azure briefing workflow **Denmark in 5**, the historical **Ariel's Pizza** operations case, agent-permission prototypes and supporting labs.

Each project identifies its implementation status and evidence limits. [Validation dates, tested revisions and commands](career-portfolio/evidence.md) are kept together so a reviewer can check the claims.

**Have an identity, security or implementation role to discuss?** [Email me](mailto:eririmo@protonmail.com). I can walk through the code, explain the tradeoffs and discuss what would be needed in your environment.
