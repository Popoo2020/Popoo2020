# Security model

This repository is a local portfolio implementation. It does not authenticate to a cloud, start a server, accept webhooks or execute cloud changes. Its data and approval identities are synthetic. Keep real employee exports, tenant data, tokens and approval records out of public issues and commits.

## Trust boundaries

| Boundary | Local behaviour | Requirement before a live pilot |
|---|---|---|
| HR event and identity | Explicit subject identifiers, provider bindings and role/status consistency | Authenticate event origin; authorize HR publishers; prevent event replay and identity substitution |
| Provider observations | Strict input shapes, source pointers, scope assertions, timestamps and query coverage | Collect every required page; verify source identity and observed resource scope; resolve relevant inherited access |
| Policy and plan | Re-derive the plan; compare policy, workforce and snapshot digests | Protect policy changes and review them separately from execution; obtain fresh state immediately before changes |
| Approval | Two distinct synthetic approver IDs, exact plan/operation/subject binding, expiry, denial and self-approval checks | Authenticate both approvers; authorize their ownership; store signed decisions; revalidate at execution |
| Cloud execution | In-memory state only; removals precede new grants; failed removal freezes grants | Per-provider executor identities, concurrency protection, asynchronous completion checks, retry journals and real read-back |
| Evidence | Consistent before/after files, audit hash chain and checksum manifest | Separate write authority, encryption, data minimization, retention and a trusted signature or external anchor |

## Threats exercised by tests

An edited plan with a newly calculated hash still has to match policy-derived operations. Approval for a different plan cannot authorize a grant. Missing approvals do not prevent already-authorized lifecycle removals in the model. A contract expiring between planning and execution invalidates the plan, including a previously valid no-op review. Local execution never refreshes the timestamp of a cloud observation.

Incomplete pagination, unresolved group assignments, unknown principal forms, ambiguous query coverage and unsupported conditional policies fail validation. JSON duplicate keys, non-finite numbers and unknown security fields are rejected. Markdown report cells escape HTML and table delimiters. The bundle verifier accepts a fixed file set and rejects symlink evidence files.

## Remaining limitations

The CLI caller controls all input files. A caller can invent an HR event or approver; a hash does not turn that assertion into authenticated authority. A provider-shaped fixture is not proof that the provider produced it. Someone who can replace an entire evidence bundle can recompute its manifest and hash chain.

The catalogue is deliberately bounded. Removal of its assignments is not proof of zero effective access: inherited rights, group expansion, resource policies, cached sessions, tokens, credentials and provider propagation need separate assessment. Disabling an identity is a local model transition, not evidence of actual session termination.

There is no distributed transaction across clouds. A partial removal is not automatically undone by restoring old privileges. A fresh observation, new plan and new grant approvals are needed for recovery. A live implementation would also need a durable execution journal, concurrency locks, protected emergency access and an operational escalation process. The code provides no production availability or response-time commitment.

## Reporting a concern

For a reproducible defect using synthetic data, open an issue in the [portfolio repository](https://github.com/Popoo2020/Popoo2020/issues) and include the project path, Python version, command and expected behaviour. For a concern that contains sensitive information, contact **eririmo@protonmail.com** first with a minimal description. Do not send credentials or real employee records. No response deadline is promised.
