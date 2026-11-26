# Official sources

Research date: **26 November 2026**. These links support design decisions and boundaries, not a claim that any live integration was tested. Provider documentation changes; recheck it before implementation. Sources are summarized, not reproduced.

## Microsoft

- **MS1 — [Configure group source of authority](https://learn.microsoft.com/en-us/entra/identity/hybrid/how-to-group-source-of-authority-configure).** Authority transfer, synchronization state and competing-write limitations. A simple sync flag is insufficient to establish every group's management path.
- **MS2 — [Revoke user access](https://learn.microsoft.com/en-us/entra/identity/users/users-revoke-access).** Directory actions, access tokens and application-owned sessions have different effects.
- **MS3 — [Graph: revokeSignInSessions](https://learn.microsoft.com/en-us/graph/api/user-revokesigninsessions?view=graph-rest-1.0).** Refresh-token/session invalidation, delay and external-user limitations.
- **MS4 — [Functions connections and managed identities](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections).** Identity-based storage connections, permissions and hosting-plan considerations.

## AWS

- **AWS1 — [Provision users and groups using SCIM](https://docs.aws.amazon.com/singlesignon/latest/userguide/provision-automatically.html).** IdP synchronization, stable identifiers and the risks of using mutating Identity Store APIs alongside SCIM. The APIs are not universally disabled.
- **AWS2 — [CreateAccountAssignment](https://docs.aws.amazon.com/singlesignon/latest/APIReference/API_CreateAccountAssignment.html).** Account/permission-set assignments for `USER` or `GROUP` principals and asynchronous completion checks.
- **AWS3 — [Authentication sessions](https://docs.aws.amazon.com/singlesignon/latest/userguide/authconcept.html).** Distinguishes portal, application and IAM role sessions after access changes.
- **AWS4 — [Lambda execution roles](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html).** Runtime role assumption and least-privilege service access.

## Google Cloud

- **GCP1 — [Workforce Identity Federation](https://docs.cloud.google.com/iam/docs/workforce-identity-federation).** External workforce principals, claim mapping and attribute conditions.
- **GCP2 — [Allow policies](https://docs.cloud.google.com/iam/docs/allow-policies).** Bindings, conditions, policy inheritance, versions and concurrency metadata.
- **GCP3 — [Access change propagation](https://docs.cloud.google.com/iam/docs/access-change-propagation).** Eventual consistency and delayed effect of policy/group changes.
- **GCP4 — [Cloud Run service identity](https://docs.cloud.google.com/run/docs/securing/service-identity).** Managed runtime tokens and separation of deployer and service identities.

## Standards and law

- **ISO1 — [ISO/IEC 27001:2022](https://www.iso.org/standard/27001)** and **ISO2 — [ISO/IEC 27002:2022](https://www.iso.org/standard/75652.html).** Public descriptions establish management-system requirements versus control guidance. The candidate mapping is project interpretation; it does not replace the licensed standards or assess all their requirements.
- **ISO3 — [ISO: certification](https://www.iso.org/certification.html).** ISO develops standards; external bodies perform certification.
- **EU1 — [Directive (EU) 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555/oj/eng).** Articles 2, 21, 26 and 41 establish scope, risk-management measures, jurisdiction and transposition timing.
- **EU2 — [ENISA: supporting NIS2 implementation](https://www.enisa.europa.eu/news/supporting-nis2-implementation-through-actionable-guidance), 26 June 2025.** Explains the nonbinding guidance's evidence approach and limited sectoral scope; national obligations remain relevant.

No labor-market forecast or job-volume claim is derived from these technical and legal sources. No provider endorsement is implied.
