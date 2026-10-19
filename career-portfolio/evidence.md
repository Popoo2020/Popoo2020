# Technical evidence — from a CV claim to the implementation

[Profile](../README.md) · [CV](ai-implementation-cv.md) · [Repository guide](README.md) · [Machine-readable verification record](verification-2026-10-19.json)

**Reviewed 19 October 2026.** Start with SundAI for a public API implementation, Sentinel for a Python workflow with decision gates, or Denmark in 5 for applied Azure architecture. Public test results below were executed locally with synthetic inputs and mocked external services. Private-project results were checked against GitHub CI records. These are dated engineering observations, not independent certification or measured business impact.

## SundAI website and enquiry API

**CV claim:** JavaScript/Cloudflare API integration, input validation, abuse controls and automated checks.

- **Implementation:** [contact API](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/2fde43b61379b57ee9d6a2b744301acf0d38377f/site/functions/api/contact.js): bounded JSON input, field/origin validation, Turnstile hostname/action checks, email routing, escaped HTML and retry handling.
- **Tests:** [validation and failure paths](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/2fde43b61379b57ee9d6a2b744301acf0d38377f/site/tests/contact-security.test.mjs) and [email routing/receipts](https://github.com/Popoo2020/Enterprise-Sundai-Bot/blob/2fde43b61379b57ee9d6a2b744301acf0d38377f/site/tests/contact-delivery.test.mjs).
- **Observed:** 114 JavaScript tests passed on Node 24.19.0; [website CI](https://github.com/Popoo2020/Enterprise-Sundai-Bot/actions/runs/38821188605) passed the same 114 tests on Node 22 at the same revision.
- **Scope:** mocked providers; this does not demonstrate live email delivery or uptime. Local/edge rate checks are implemented; a globally atomic rate cap is not established.

From that repository's root: `node --test site/tests/*.test.mjs`.

## Sentinel AI AutoTriage

**CV claim:** Python recommendations pass through redaction, validation, deterministic policy checks, approval gates and audit logging.

- **Implementation:** [workflow](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/4f7f3835a2975a3de96ef1120d8c4867d987ab6f/src/auto_triage.py), [policy](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/4f7f3835a2975a3de96ef1120d8c4867d987ab6f/src/recommendation_policy.py), [Azure SDK adapter](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/4f7f3835a2975a3de96ef1120d8c4867d987ab6f/src/sentinel_client.py).
- **Tests:** [workflow gates](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/4f7f3835a2975a3de96ef1120d8c4867d987ab6f/tests/test_auto_triage.py), [provider redaction](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/4f7f3835a2975a3de96ef1120d8c4867d987ab6f/tests/test_llm_client.py), [actual SDK objects with mocked operations](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/blob/4f7f3835a2975a3de96ef1120d8c4867d987ab6f/tests/test_sdk_integration.py).
- **Observed:** 48 tests passed locally; [GitHub CI at the published revision](https://github.com/Popoo2020/Sentinel-AI-AutoTriage/actions/runs/39241641427) also passed its test, Ruff, Bandit and dependency-audit steps. Four authored benchmark cases matched their expected parsing/policy outcomes.
- **Engineering improvement:** the 19 October review exposed SDK-field mismatch and false success reporting on failed writes. Five new regression cases cover the adapter contract and outcomes; recommendation logs now omit free-text model comments.
- **Scope:** controlled-demo prototype. No live Azure tenant or model calls were tested. Approval uses a local token, not an authenticated, durable per-incident approval service. A timed-out write requires reconciliation before retrying.

From that repository's root, in a fresh Python environment:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
python -m src.benchmark
```

## Denmark in 5

**CV claim:** Python/FastAPI briefing workflow, publication checks, Azure/Bicep and GitHub Actions/OIDC delivery.

- **Review:** [architecture](../case-studies/denmark-in-5-azure/README.md), [engineering decisions](../case-studies/denmark-in-5-azure/engineering-review.md), [generalised implementation patterns](../case-studies/denmark-in-5-azure/implementation-excerpts.md) and [editorial assurance](../case-studies/denmark-in-5-azure/editorial-assurance.md).
- **Observed in private CI:** the 19 October completion release passed **875 Python tests** and **23 editorial acceptance cases**, plus compile, Ruff and Bandit checks. The acceptance cases overlap the regression suite; they must not be added together as 898 independent tests.
- **Evidence:** [public validation record](../case-studies/denmark-in-5-azure/evidence/editorial-validation-2026-10-19.json). Application source and raw execution records remain private. Public snippets explain selected patterns; they are not the complete runnable application.
- **Scope:** offline regression results and historical infrastructure deployment evidence. Current delivery readiness, factual accuracy and readership require their own verification. The approximately one-minute routine input figure is an operator estimate, not a timed study or total maintenance effort.

## Supporting public modules

| Module | Read the implementation | Observed result | Scope |
|---|---|---|---|
| Agent policy decisions | [Policy engine](https://github.com/Popoo2020/Secure-Agent-Control-Plane/blob/ff77aedd5cec54885340c3dbbff680a8bcfb59f3/src/policy_engine.py) · [tests](https://github.com/Popoo2020/Secure-Agent-Control-Plane/tree/ff77aedd5cec54885340c3dbbff680a8bcfb59f3/tests) | 7 tests passed | Decision library; no live tool broker or external identity integration. |
| Retrieval-security evaluation | [Evaluator](https://github.com/Popoo2020/RAG-Security-Eval-Harness/blob/42c9b63bfcab3073bfcd9a5cce703065ea507490/src/evaluator.py) · [metrics/tests](https://github.com/Popoo2020/RAG-Security-Eval-Harness/blob/42c9b63bfcab3073bfcd9a5cce703065ea507490/tests/test_metrics.py) | 6 tests passed | Small deterministic regex/trust-label baseline; seven authored sample cases are not a real-world accuracy benchmark. |
| Governance reporting | [Report generator](../ISO42001-AI-Governance-Evidence-Toolkit/src/generate_readiness_report.py) · [tests](../ISO42001-AI-Governance-Evidence-Toolkit/tests/test_generate_readiness_report.py) | 4 tests and report-generation checks passed | Illustrative registers and reporting; not an organisational certification or compliance audit. |
| DevSecOps reference | [Workflow](https://github.com/Popoo2020/DevSecOps-Reference-Pipeline/tree/b2a5eaf0fa4e8ed1e1ac30560990858bc1324e1b/.github/workflows) | Workflow inspected | Reusable conditional checks. The smoke test is a placeholder; dependency auditing runs only when a requirements file exists. |

To repeat the policy/evaluation tests, check out the revision in the [verification record](verification-2026-10-19.json), install that repository's `requirements.txt` and `pytest`, then run `python -m pytest -q tests`. For governance reporting, run `make validate` inside `ISO42001-AI-Governance-Evidence-Toolkit` (Python standard library only). Use a separate environment for each repository.

## Business experience and evidence boundaries

[Ariel's Pizza](../case-studies/ariels-pizza-operations/README.md) describes a historical implementation across **three locations**, based on my builder/operator account. Source, customer/employee records and transfer documents are not public. **45+ staff** describes my management scope at Varha. These numbers describe scale, not measured productivity gains. Education, language proficiency and employment history are candidate background; passing repository tests does not independently verify them.

For a technical conversation, I can explain the requirement, walk through the code and tests, and discuss what would be needed for a production handover. [Contact](mailto:eririmo@protonmail.com).
