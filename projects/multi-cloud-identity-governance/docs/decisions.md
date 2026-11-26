# Design decisions

## 1. Begin with a workforce move

The initial case is a person moving from order operations into finance. It has a business owner, an old role, a new role, incompatible access and a clear review outcome. Joiner, leaver, contractor expiry and periodic review reuse the same model. Machine identities, privileged elevation and full enterprise IGA are separate future scopes.

## 2. Use an explicit entitlement catalogue

A logical entitlement maps to a provider, resource, permission, owner and mutation authority. The engine never equates Entra groups, AWS permission sets and GCP roles merely because their display names look alike. Immutable identity bindings connect the workforce subject to provider principals. Unsupported assignments require review instead of being silently dropped.

## 3. Validate saved exports before adding collectors

The first version uses strict normalizers and an import bridge. Coverage is declared separately from query results, so an empty AWS response cannot be interpreted without knowing which account and permission set was queried. This produces a repeatable, credential-free demonstration. It trades live integration proof for a small surface reviewers can inspect. A live collector is complete only after authorized provider testing and collection evidence.

## 4. Separate revocation from grant approval

An authoritative lifecycle record justifies removal of no-longer-needed assignments in the model. New assignments require the manager and a separate resource owner. Every approval binds to one operation, subject and plan. Policy, workforce or state changes invalidate the plan; crossing a contractor's expiry requires replanning even if the original plan was a no-op.

## 5. Prefer containment over pretending changes are atomic

All planned removals run before grants. Any failed removal freezes all new grants, while successful removals remain in place. A failed grant can leave a partial target role. This is visible in the report and requires a new plan. Automatic restoration of old permissions could reintroduce an access conflict; there is no cross-cloud rollback transaction.

## 6. Use deterministic policy decisions

There is no language model in the authorization path. Exact identities, ownership, time limits and policy checks determine the outcome. AI could later help summarize evidence for a reviewer, but its narrative must not authorize grants or change the underlying facts.

## 7. Make evidence inspectable and honest

Reports link findings to plans, approvals, before/after state and operation outcomes. Control IDs are project identifiers; the ISO/NIS2 mapping is a limited interpretive cross-reference. Hashes support reproducibility and local modification detection. Independently trusted signatures, immutable retention and authenticated approvals belong to a live service design.

## 8. Keep the runtime small

Python's standard library is sufficient for this bounded simulation and JSON import contract. No cloud SDK or network dependency is needed to run it. Provider collectors, durable orchestration and deployment infrastructure can be developed separately without making the portfolio demo require three paid cloud environments.
