# Security, privacy and human oversight — Ariel's Pizza

**Scope:** this is a threat review of the **new October 2026 synthetic offline demonstration**, not a security audit of the historical 2024–2025 implementation.

## Trust boundaries and relevant assets

A real system would involve ordering platforms, staff, managers, model providers and messaging services. Sensitive assets could include customer/order records, employee availability, access tokens, messaging sessions and manager approvals. The public sample contains **none** of these; it accepts invented aggregate facts and categorical values only.

## Controls implemented and tested in the new sample

1. **Allowlisted schema:** reject unexpected fields, arbitrary free text, personal names, phone numbers, order identifiers and staff absence reasons.
2. **Synthetic site and source checks:** only three fictional site aliases and expected adapter labels.
3. **Bounded data:** fixed item, role and complaint enums; integer limits; booleans cannot masquerade as counts.
4. **Human-in-the-loop:** low stock, staffing gaps and complaints require manager review; routine stock status remains advice.
5. **No dispatch:** approval only changes an in-memory state. No API, message, purchase, compensation, Trello task or WhatsApp call exists.
6. **Local idempotency:** duplicate identical event IDs do not create another recommendation; conflicting reuse fails.
7. **Audit minimisation:** only synthetic IDs, rule names and lifecycle actions are recorded, never raw payloads.

The demo manager role is a **string parameter**, not authenticated identity. The ledger is **not persistent**. These are illustrative controls, not production assurance.

## Threat and gap register

| Threat | Demonstrated mitigation | Needed before production |
|---|---|---|
| Prompt injection or malicious payload | No free text, strict validation | Authenticated ingestion and model isolation |
| Staff/customer privacy exposure | No real personal data in schema | GDPR legal basis, retention, RBAC, secure deletion |
| Unauthorised managerial action | Offline role-string check; no external effects | Strong identity, role/branch permissions, approval provenance |
| Duplicate notifications/purchases | No outbound calls; in-memory dedup | Durable transactional outbox and delivery reconciliation |
| Unavailable Wolt/OpenAI/WhatsApp | No provider dependencies | Circuit breakers, retry budgets, safe fallbacks |
| Sensitive logging | Synthetic metadata-only audit | Access-controlled log storage, retention and alerting |

## Historical and intellectual-property boundaries

The original system is reported to have used Python/OpenAI with Wolt/ordering APIs, Trello, Google Sheets and WhatsApp. Its historical permissions, encryption, secrets, staff consent, retention and messaging safety were **not independently inspected**. Do not attribute the new sample's exact safeguards to that original tool.

No proprietary code transferred with the business sale, live credentials, private operational data, employee messages, real customer information or production account identifiers are published. Future integration would require contractual/IP authorisation, privacy/security review and authenticated approval.

[Case study](README.md) · [Architecture](architecture.md) · [Evidence and limitations](evidence-and-outcomes.md)
