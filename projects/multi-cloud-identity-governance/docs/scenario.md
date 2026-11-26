# Scenario: Fjord Supply

Fjord Supply is a **fictional 180-person B2B distributor**. Its workplace and order applications use Microsoft Entra identities, AWS hosts order integrations, and Google Cloud hosts analytics. The repository models selected assignments for four synthetic people; it does not contain 180 employee records, customer data or a production deployment. The source of the scenario is [examples/scenario.json](../examples/scenario.json).

## The business problem

An employee changes responsibilities, but old access survives alongside new access. A contractor's account remains usable after the engagement ends. A manager agrees that access is needed, yet nobody records which resource owner approved it. Later, a reviewer cannot distinguish an attempted removal from a completed change.

The project makes these questions explicit: what access is justified now, who owns the decision, which changes are safe to attempt, and what evidence explains the outcome? The role catalog is a business policy, not an inference from whatever permissions happen to exist.

## Cases in the fixture

The fixed evaluation time is **26 November 2026, 09:00 UTC**; the initial snapshot is five minutes old.

| Case | Intended local outcome |
|---|---|
| `emp-014`, operations to finance | Retain `azure.staff`; remove `azure.order_ops`, `aws.order_operator` and `gcp.sales_viewer`; then add three finance entitlements with manager and owner approval. |
| `emp-015`, joiner | Add the four entitlements of `order_operations`, subject to approval. |
| `emp-019`, departed employee | Simulate identity disablement and remove the four catalogued assignments. |
| `contractor-007`, expired engagement | The contract ended at 08:00 UTC. Simulate disablement and remove vendor-portal and AWS support access. |
| Access review of `emp-014` | Remove excess assignments and report missing ones. Review does not automatically grant missing access. |

Two explicit separation-of-duties rules prohibit combining AWS order operation with GCP finance access, and the order application with the finance application. These are demonstration policy choices. They are not a universal legal rule or a complete fraud-control model.

## Ownership for a future pilot

This RACI describes proposed responsibilities; fixture approval names are not authenticated people. A = accountable, R = responsible, C = consulted, I = informed.

| Activity | A | R | C / I |
|---|---|---|---|
| Maintain workforce facts | HR owner | HR operator | Manager C; IAM operator I |
| Approve new access | Resource owner | Manager and resource owner | Security C; IAM operator I |
| Execute and reconcile changes | IAM service owner | IAM operator | Resource owner C; manager I |
| Review evidence and exceptions | Security owner | Assigned reviewer | HR, resource owner and IAM operator C |

## Pilot acceptance goals — not measured results

For a future isolated pilot, target: every grant has valid manager and owner approval; zero new grants follow a failed removal; every changed assignment has a verified outcome or named unresolved exception; and a reviewer can reconstruct each sampled case from its bundle within five minutes. Measure actual propagation and completion times before choosing an operational SLA. No labor savings or ROI are claimed.

Provider workflows already require identity ownership, assignment management and careful revocation. NIS2 includes access-governance and effectiveness-assessment requirements. Those needs explain this portfolio problem, without establishing that this distributor is legally in scope or predicting employment demand. See [control mapping](control-mapping.md) and [sources](sources.md).
