# Engineering decisions and validation

[Case study](README.md) · [Implementation patterns](implementation-excerpts.md) · [Evidence](evidence/README.md) · [Disclosure scope](public-disclosure.md)

**Reviewed:** October 2026. **Scope:** source, historical deployment records and selected execution evidence for the Azure delivery component. This is a portfolio review, not an independent penetration test.

## Decisions linked to operational needs

| Need | Implemented response | What the evidence establishes |
|---|---|---|
| Repeatable infrastructure | Bicep definitions for the VM and network components. | Infrastructure-as-code and a recorded successful deployment. |
| Avoid a directly addressable VM endpoint | No public-IP association in the NIC definition. | A template property; not a complete network-security assessment. |
| Authenticate deployment without an Azure client password | GitHub-to-Azure OIDC federation. | A reviewed authentication flow and successful historical login. |
| Keep application credentials out of source | GitHub Actions Secrets and separate messaging session storage. | Distinct credential paths, not a claim of independent vault isolation. |
| Preserve the selected edition | Artifact provenance, integrity and publication checks. | Delivery eligibility checks; not automatic verification of every news claim. |
| Handle an uncertain send | A persistent journal and reconciliation before another attempt. | Duplicate-risk controls; not an exactly-once delivery guarantee. |
| Limit unnecessary compute use | Readiness checks and a deallocation cleanup path. | An implemented operating control; not measured savings or a zero-cost promise. |

## Delivery behaviour

The bridge validates the edition and approved destination before sending. It records a pending attempt before asking the transport to deliver. A confirmed outcome updates the journal; an uncertain outcome is reconciled rather than treated as permission to resend blindly.

This separates three questions: was the content accepted, was delivery attempted, and was its outcome confirmed? Keeping those states distinct is useful for debugging, user trust and operational handover.

## Validation boundaries

The historical record includes successful Azure authentication, deployment preview, VM/network deployment and host-initialisation steps. A separate infrastructure CI run passed shell-syntax, YAML-parsing and Bicep-compilation checks.

These checks do not establish current end-to-end delivery, restore capability, effective tenant permissions or comprehensive host hardening. A workflow conclusion must be interpreted with its job and step outcomes; skipped delivery is not proof of delivery.

The messaging integration uses WhatsApp Web through an unofficial client library. Client changes, account restrictions and session validity are operating dependencies. A production engagement needs its own transport and support decision. See the [upstream project](https://github.com/wwebjs/whatsapp-web.js).

## Further engineering work and acceptance criteria

These are proposed increments, not completed controls or a public inventory of live weaknesses.

| Increment | Evidence required before calling it complete |
|---|---|
| Controlled end-to-end verification | An authorised test destination, confirmed delivery and cleanup, using synthetic content and avoiding duplicate publication. |
| Permission-boundary review | Intended versus effective roles, job-scoped permissions and allowed/denied operation checks. |
| Recovery and session-lifecycle exercise | An isolated restore test and documented revocation, re-pairing and recovery ownership. |
| Monitoring and cost controls | A controlled failure produces an actionable alert; cleanup and continuing resource costs are reviewed. |

Exact permission assignments, administrative paths, session implementation details, operational incidents and recovery commands belong in restricted operational documentation. The public case study retains the decisions, evidence boundaries and safe review criteria.

## Azure skills demonstrated

The component provides practical examples of infrastructure-as-code, virtual networking, federated authentication, credential handling and deployment validation. It complements Azure security training. It does not establish a vendor certification, a full Azure security baseline or enterprise production tenure.

Primary references: [GitHub OIDC for Azure](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure), [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use), [Azure RBAC guidance](https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices), [VM states and billing](https://learn.microsoft.com/en-us/azure/virtual-machines/states-billing).

[Back to the case study](README.md)
