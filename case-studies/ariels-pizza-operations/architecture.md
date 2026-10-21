# Architecture and decision data flow — Ariel's Pizza

**Two distinct layers:** (1) the historical functionality described by the founder/operator, and (2) a newly authored October 2026 offline example. This is **not** a recovered production design or transferred source code.

## Historical functional architecture — operator account

~~~mermaid
flowchart LR
  O[Wolt and ordering data] --> P[Python operations assistant]
  M[Manager priorities] --> P
  T[Trello and Google Sheets] <--> P
  P <--> A[OpenAI assistance]
  P --> D{Human decision needed?}
  D -->|Routine guidance| W[Staff via WhatsApp]
  D -->|Uncertain / consequential| R[Manager response]
  R --> P
~~~

The original system's API payloads, authentication, storage, hosting, retention, security settings and delivery receipts have **not** been independently inspected. This diagram captures functional relationships, not verified infrastructure.

## New offline reference flow (2026; not historical)

~~~mermaid
flowchart TD
  I[Invented aggregate event] --> V[Strict schema validation]
  V -->|Unexpected fields| X[Reject with no side effects]
  V --> E[Deterministic rule engine]
  E --> D{Manager judgement required?}
  D -->|No| A[Routine in-memory advice]
  D -->|Yes| H[Review-required state]
  H --> M{Explicit demo manager decision}
  M -->|Approve / reject| R[In-memory resolution only]
  A --> L[Minimal audit metadata]
  R --> L
  L --> O[JSON demo output; no outbound connectors]
~~~

No LLM is called in the sample. This deliberately tests the **policy boundary** independently of the historical AI implementation.

## Event contract and human oversight

| Synthetic event | Allowlisted facts | Decision | External action |
|---|---|---|---|
| Inventory | item, stock, reorder_point | Low stock → manager review; otherwise routine advice | None |
| Shift gap | role, open_slots | Manager review before any staff outreach | None |
| Complaint | issue, severity | Manager review before response or compensation | None |

All events also require a synthetic demo identifier, site alias SITE_A/B/C and matching adapter type. Unknown fields, personal data, free text, invalid values and unexpected sources are rejected. Reused identical event IDs return the existing decision; conflicting reuse is rejected. The ledger is **in memory**, not durable.

## Production boundaries not implemented

| Risk | Demo safeguard | Production requirement |
|---|---|---|
| Malicious or inaccurate events | Allowlisted typed facts | Authenticated adapters, input signatures, source verification |
| Prompt injection | No free-text or model | Isolated model output and independent policy validation |
| Unauthorised approval | Demo manager-role string | Real authentication, RBAC, per-site authorisation |
| Duplicate side effects | No outbound calls; local dedup | Durable idempotency, transactional outbox, receipts |
| Personal data exposure | Invented aggregate-only fixtures | GDPR review, data minimisation, retention/deletion |
| Provider outage | No external providers | Timeouts, bounded retries, monitoring and reconciliation |

An in-memory approval is **not** a purchase, task creation, message or customer refund. Neither this code nor its tests prove the original historical implementation used these controls.

[Case study](README.md) · [Demo](demo/README.md) · [Security review](security-and-oversight.md)
