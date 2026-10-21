# Synthetic offline operations assistant — independent 2026 demonstration

**NOT historical Ariel's Pizza source. NOT connected to live accounts.**

This small Python standard-library example illustrates a principle from the historical operator account: **turn structured operational signals into recommendations, while keeping consequential decisions with a manager**. It does not reconstruct the original tool, copy its API integrations, invoke OpenAI or simulate real employees/customers.

## Run locally

From the case-study directory (Python 3.11+):

~~~bash
python -m demo.scenarios
python -m unittest discover -s demo/tests -v
~~~

No third-party dependencies, credentials or environment variables are needed. The CLI prints JSON. It performs **no network calls, file writes, outbound notifications, purchases or external side effects**.

## Invented scenarios

| Scenario | Synthetic input | Expected output |
|---|---|---|
| Low inventory | SITE_A, cheese stock 3 versus threshold 8 | STOCK_REVIEW → manager review; illustrative approval |
| Shift gap | SITE_B, one kitchen slot | SHIFT_REVIEW → manager review; no staff contact |
| Complaint | SITE_C, high-priority wrong item | CUSTOMER_CARE_REVIEW → manager review; no refund or message |

All site names, event IDs, quantities and issue types are invented. [sample-output.json](sample-output.json) is a deterministic snapshot of the CLI output.

## Code and assurance

- [engine.py](engine.py): allowlisted schema, deterministic rules, local idempotency, demo manager-only resolution, metadata-only audit.
- [scenarios.py](scenarios.py): three labelled fixtures, one in-memory illustrative manager approval and JSON output.
- [tests/test_engine.py](tests/test_engine.py): regressions for accepted/rejected inputs, private fields, duplicate events, unauthorised approvals and safe output.

A manager approval is recorded as `approved_for_demo` and **never dispatches** a message or purchase. The `actor_role` string is a test stub, **not authentication**. The event ledger is process-local, **not durable**.

## Production controls deliberately out of scope

Real source/user authentication; branch-specific RBAC; encrypted credentials; actual API contracts; GDPR retention/deletion; durable event deduplication and transactional outbox; supplier outages; delivery receipts; monitoring; contract/IP permission. None of these are claimed to be implemented by this sample.

[Case study](../README.md) · [Architecture](../architecture.md) · [Security and oversight](../security-and-oversight.md) · [Evidence](../evidence-and-outcomes.md)
