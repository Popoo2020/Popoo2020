# Access review: mover

**Synthetic demonstration. No cloud account was changed.**

- Scenario: Fjord Supply (fictional)
- Subject: `emp-014`
- Outcome: **completed_simulation**
- Plan: `e40ff79511343a3d9a9ec351a5314877718e6af9566d0b3a09d2bd5bd3cac2b7`
- Source observation time: `2026-11-26T08:55:00Z` (not refreshed by simulation)
- Scope: catalogued direct assignments; inherited/effective access and active sessions are outside the check.

## What happened

The workflow simulated **3 removals** and **3 grants**. It recorded **0 failures** and **0 blocked operations**.

| Provider | Action | Assignment | Result | Reason |
|---|---|---|---|---|
| aws | revoke | Order integration operator | simulated | No longer justified by the authoritative workforce record |
| azure | revoke | Order operations application | simulated | No longer justified by the authoritative workforce record |
| gcp | revoke | Sales analytics project viewer | simulated | No longer justified by the authoritative workforce record |
| aws | grant | Cost and billing read-only | simulated | Bound, unexpired demo approvals present; identities are not authenticated |
| azure | grant | Finance reporting application | simulated | Bound, unexpired demo approvals present; identities are not authenticated |
| gcp | grant | Finance analytics reader | simulated | Bound, unexpired demo approvals present; identities are not authenticated |

## Remaining work

- Unexpected assignments: none in the model
- Missing role assignments: none in the model
- Live access and session revocation: **not verified**.

## Control evidence

`model_checked` means the local policy check succeeded. It is not a compliance opinion.

| Control | Outcome | Finding | Evidence |
|---|---|---|---|
| IG-01 — Identity and scope | model_checked | Subject, policy and bounded snapshot are linked by immutable identifiers and digests. | [plan.json](plan.json), [before.json](before.json) |
| IG-02 — Role reconciliation | model_checked | 0 unexpected and 0 missing assignments remain in the catalogued scope. | [before.json](before.json), [after.json](after.json), [result.json](result.json) |
| IG-03 — Approval before grants | model_checked | New grants require two distinct, plan-bound, unexpired manager and owner approvals in the model. | [approvals.json](approvals.json), [result.json](result.json) |
| IG-04 — Separation of duties | model_checked | 0 configured conflicts remain after simulation. | [plan.json](plan.json), [result.json](result.json) |
| IG-05 — Departure and expiry | not_applicable | Departure and expiry events plan IdP disablement and removal of catalogued assignments; existing sessions are not tested. | [plan.json](plan.json), [after.json](after.json), [result.json](result.json) |
| IG-06 — Review evidence | generated | A local hash chain and file manifest support reproducible integrity checks, not independent authenticity. | [audit.jsonl](audit.jsonl), [manifest.json](manifest.json) |

## Reviewer actions

- **IG-01:** For a pilot, validate HR authority, collection coverage and identity bindings with their owners.
- **IG-02:** Resolve failed removals; collect new state and replan before requesting approvals for new grants.
- **IG-03:** Replace synthetic approval assertions with authenticated, signed decisions before live execution.
- **IG-04:** Have business owners review the conflict rules and any wider inherited access.
- **IG-05:** Verify actual disablement, SCIM propagation, credential handling and session expiry using each provider's supported controls.
- **IG-06:** Use separated evidence writers, retention controls and a trusted signing or anchoring service in a pilot.

## Evidence limits

All identities, approvals and provider outcomes are invented for this exercise. Provider exports are not collected or authenticated by this run. Checksums and the hash chain detect changes relative to the supplied bundle; someone who can rewrite the entire bundle can recompute them. Neither ISO certification nor legal compliance is established.
