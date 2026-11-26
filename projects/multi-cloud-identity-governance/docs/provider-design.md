# Provider design and deployment boundaries

Design reviewed: **26 November 2026**. See the [official sources](sources.md).

## What runs here

This repository contains a deterministic Python simulator and thin normalizers for selected provider-shaped JSON exports. It does not collect live cloud data, authenticate to a tenant, deploy infrastructure, or change cloud permissions. A normalized fixture describes observed assignments; it is not a complete calculation of effective access.

The current [normalizer contract](../identity_governance/providers.py) is deliberately narrow:

| Import | Accepted scope |
|---|---|
| Entra/Azure | Direct user-to-group membership from a complete, group-only `memberOf` response. No authority validation or transitive expansion. |
| AWS | Direct `USER` assignments for one account and permission set. Group assignments and unfinished pages are rejected. |
| Google Cloud | Unconditional bindings for supported individual principals on one resource. Conditions, groups, principal sets and inherited-policy envelopes are rejected. |

These adapters do not authenticate their inputs. Rejecting a pagination marker cannot detect pages omitted by an upstream exporter. The broader collection and execution behavior below is future design.

The implemented [import bridge](../identity_governance/imports.py) checks immutable principal bindings and explicit catalogue coverage before passing a snapshot to the planner. The [synthetic export bundle](../examples/export-bundle.json) covers one Azure tenant, three AWS account/permission-set queries and one GCP resource. Two AWS results are empty but still require an explicit query scope. Provenance records preserve export pointers and digests. Declared coverage is not proof that a collector returned all real cloud data.

The fictional customer is a 180-person European distributor. The small dataset represents selected cases, not a complete workforce inventory. HR owns employment status, department, manager and contractor end dates. Resource owners approve business access. Stable person and provider identifiers link records; email addresses alone are unsuitable identity keys.

The cases cover a joiner, an employee moving from sales/operations into finance, contractor expiry, a leaver and access review evidence. The mover must lose incompatible old access before receiving approved finance access. A genuine production implementation would first agree this business rule with owners, including any justified transition period.

## Decisions, execution and evidence

The local plan compares the event's desired access with a snapshot. Grants require manager and resource-owner approvals bound to the plan hash and an expiry. A snapshot digest prevents execution against changed local state. Removals precede grants; a failed removal freezes new grants. Results distinguish `completed_simulation`, `partial_simulation` and `blocked_simulation`.

Approval identities are caller-supplied fixture values. Checking a name, approval role and hash is **not authentication of an approver**. A live service needs authenticated approvers, authorization against an independently maintained owner registry, separation of requester and approver where required, expiry checks and replay protection.

The demo writes `plan.json`, `approvals.json`, `before.json`, `after.json`, `result.json`, `assessment.json`, `audit.jsonl`, `report.md` and `manifest.json` under `build/demo/<scenario>/`; the successful mover and failed-removal examples are committed under `examples/output/`. The audit SHA-256 chain and file manifest detect inconsistencies against supplied hashes. Someone able to rewrite the whole bundle can recompute them. They are not independent signatures, trusted timestamps or tamperproof storage.

Live recovery must preserve confirmed removals when another step fails. Freeze grants, retain partial outcomes, reconcile actual state and retry idempotently. Do not automatically restore obsolete sales access to make a failed finance transition look atomic. Any compensating regrant needs fresh justification and approval. This repository does not implement a distributed rollback transaction.

## Provider semantics

### Microsoft Entra ID and Azure

Use the group inventory's recorded authority. Assigned cloud-managed groups can have an Entra-owned membership workflow. Groups controlled by an upstream directory must be changed there; dynamic groups require their rule/attribute workflow. Do not infer ownership solely from `onPremisesSyncEnabled`: Microsoft now supports explicit group authority transfers, with additional state and synchronization requirements. This project does not perform such transfers. [MS1](sources.md#microsoft)

An eventual Graph collector must retrieve complete user/group/membership pages, preserve stable IDs and provenance, and distinguish direct membership from inherited or transitive access. Group membership, Entra directory roles, application assignments and Azure resource RBAC are different resources. A group export alone does not inventory all four.

A future executor should be restricted to approved group objects and operations, with separate permission review for role-assignable groups. Removing membership, disabling an account and revoking refresh tokens are distinct actions. Application-issued sessions may survive directory changes; Graph session revocation also has limitations for external users. Report the action and verification scope, never “all access immediately revoked.” [MS2–MS3](sources.md#microsoft)

### AWS IAM Identity Center

The scenario uses an external IdP with SCIM provisioning. That IdP owns synchronized group membership. The planner must route membership changes upstream and wait for read-back after synchronization. **This project's policy prohibits direct Identity Store mutations of SCIM-owned groups.** AWS technically leaves mutation APIs accessible; competing writers risk divergence from the IdP. This is an ownership rule, not an API impossibility. [AWS1](sources.md#aws)

A direct `USER` permission-set assignment is a separate resource identified by account, permission set and principal. It can be planned separately through the IAM Identity Center assignment APIs. Deleting a shared `GROUP` assignment to remove one employee would affect everyone in that group and is not the intended operation. Assignment requests are asynchronous: submission is not confirmed completion. [AWS2](sources.md#aws)

An eventual collector must join identity-store users and memberships to account assignments, including direct assignments. Removing future assignment eligibility does not invalidate every existing IAM role session. Emergency session containment needs a separately authorized runbook; the simulator performs none. [AWS3](sources.md#aws)

### Google Cloud

Workforce Identity Federation maps external human identities and claims to workforce-pool principals. It is distinct from workload authentication for the service running this application. IdP group claims remain governed upstream; the normalizer does not create or delete Google user accounts. [GCP1](sources.md#google-cloud)

A resource allow-policy binding associates principals with a role, possibly under a condition. Preserve the principal URI, resource, role, condition, policy version and `etag` when designing a collector. A project-level binding is not effective-access proof: ancestor grants, deny policies, principal restrictions, groups, conditions and service-account impersonation paths can affect the result. Unsupported conditional or inherited cases require review, not a claim of complete revocation. [GCP2](sources.md#google-cloud)

Use read/modify/write with the current `etag` in any future policy writer; never replace unrelated bindings with a fixture. IAM changes propagate asynchronously, and removing one binding does not establish that every credential or alternative access path is unusable. [GCP2–GCP3](sources.md#google-cloud)

## Cloud deployment design — future work

These are alternative hosting designs for the same workflow, not three deployed services. Keep provider credentials out of code and configuration files.

| Hosting option | Processing and state | Runtime identity |
|---|---|---|
| Azure | Functions workers; Storage Queues; Table Storage for workflow state; Blob Storage for evidence | Separate managed identities. Select a hosting plan and storage extensions supporting identity-based connections; Flex Consumption avoids the Azure Files connection-string dependency. |
| AWS | Lambda workers; SQS; DynamoDB state; S3 evidence | Separate execution roles with narrowly scoped service permissions and temporary credentials. |
| Google Cloud | Cloud Run workers; authenticated Pub/Sub delivery; Firestore state; Cloud Storage evidence | Dedicated runtime service accounts and managed tokens; separate deployer identity; no downloaded service-account keys. |

These identity mechanisms are documented by the providers. Cross-cloud access would require separately configured trust and short-lived federation, not reuse of one powerful credential. Existing IdP provisioning connections remain independently administered. [MS4](sources.md#microsoft), [AWS4](sources.md#aws), [GCP4](sources.md#google-cloud)

Separate a read-only collector, a planner without provider write rights, and an executor restricted to approved targets. Evidence readers must not gain execution authority. Production queues need deduplication, bounded retries, dead-letter handling and per-identity ordering. State changes need concurrency checks; evidence needs restricted access, retention and independent integrity anchoring.

Before enabling any live write: implement pagination and incomplete-snapshot detection, authorize the exact API permissions, test throttling and partial failures in an isolated tenant/account/project, authenticate approvals, and verify resulting access at the relevant resources. None of those cloud validation steps is claimed by a successful local simulation.
