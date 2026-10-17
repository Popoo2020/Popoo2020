# Engineering review

[Case study](README.md) · [Code excerpts](implementation-excerpts.md) · [Evidence](evidence/README.md)

**Review date:** 17 October 2026  
**Scope:** the existing Azure delivery component and its GitHub/WhatsApp interfaces.  
**Method:** source inspection, historical workflow/job/log inspection and comparison with primary platform documentation. This is a portfolio engineering review, not an independent penetration test or certification audit.

## 1. Design decisions and their consequences

| Decision implemented | Reason it fits this component | Consequence to manage |
|---|---|---|
| Persistent Ubuntu VM and disk | The browser-based transport needs a reusable linked-device session and delivery journal. | One host and one persistent state location create recovery and availability dependencies. |
| Bicep-managed VM, NIC, subnet, VNet and NSG | Makes the infrastructure definition reviewable and versioned. | Template deployment is not continuous drift detection. |
| No public IP attached to the VM NIC | Avoids a directly addressable public VM endpoint. | Outbound internet access remains enabled; default NSG rules still allow VNet traffic. This is not microsegmentation. |
| GitHub OIDC for Azure access | Avoids an Azure client password in the reviewed workflow. | Trusted workflows can still obtain powerful tokens; repository, branch and environment protection matter. |
| Resource-group-scoped Contributor in bootstrap | Limits the intended deployment scope to this workload's resource group. | Contributor is broad within that scope. Bootstrap code does not prove that no other effective roles exist in the live tenant. |
| Confirmed artifact as the bridge input | Separates news generation from distribution and preserves the selected edition. | Provenance and digest checks protect artifact selection; they do not prove that every news claim is true. |
| Deallocate after an attempt | Reduces time spent in billable VM compute states. | Disk costs remain. Workflow cancellation, unavailable Azure access or cleanup failure can prevent deallocation. |

The source explicitly sets `defaultOutboundAccess: true`. There is no NAT Gateway, Azure Firewall or egress allowlist in this template. Any move to explicit outbound routing should account for browser, GitHub and package-update dependencies. See Microsoft's [NSG defaults](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview) and [outbound connectivity guidance](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/default-outbound-access).

## 2. Identity, secrets and the actual trust boundaries

**Application credentials.** The Python workflow references model-provider and Telegram secrets through GitHub Actions. These values are separate from repository source and are not injected into the reviewed bridge job. This is separation of storage and consumption, not a claim of independently isolated vaults for every component.

**Deployment identity.** The bootstrap configures an Entra application/service principal and a federated credential tied to the repository's main-branch OIDC subject. The workflow uses `azure/login` with `id-token: write`. That GitHub permission enables token requests; Azure RBAC determines what the resulting identity may do. Successful OIDC login was observed in the deployment job. The delivery workflow declares OIDC permission at workflow scope, so the bridge job also inherits token-request capability. Job-specific permissions and separate deployment/runtime identities are therefore a concrete improvement. Live effective permissions and protection rules were not exhaustively audited.

**VM identity.** A system-assigned managed identity is configured. The reviewed template does not assign it application data-access roles, and the bridge does not demonstrate using it to retrieve secrets. Enabling an identity is distinct from integrating it into the application's authentication path.

**WhatsApp authentication.** LocalAuth keeps a browser profile on persistent disk. The authentication directory is configured for the service account with mode 0700. The bootstrap also changes the bridge environment file to mode 0640. These are intended filesystem controls, not a fresh attestation of current host permissions. QR pairing is an explicitly enabled administrative operation; ordinary delivery defaults to pairing disabled. The runner and bridge share an OS identity, so workflow execution is a sensitive trust boundary.

**SSH.** Password authentication is disabled in the VM definition. The bootstrap retains the private key on the operator host and passes only the public key to deployment. No deployed Bastion resource or Bastion-only SSH NSG rule is established by this template.

References: [GitHub OIDC for Azure](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure), [GitHub Actions Secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets), [managed identities](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview), [Azure RBAC guidance](https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices).

## 3. Delivery integrity and failure handling

The reviewed bridge validates artifact origin, allowed workflow, main branch, run association, artifact name, SHA-256 digest and current-day publication metadata. It also checks the publication flags before accepting the content.

The destination is pinned by group identity. The transport revalidates that destination and administrator membership after reconnecting. The delivery code writes a pending journal entry before requesting a send, then looks for a matching outgoing message and acknowledgement before marking delivery as confirmed.

If the outcome is ambiguous, reconciliation reads history instead of blindly repeating the send. This is a concrete duplicate-risk control; it is not an exactly-once guarantee for an external messaging system.

The lifecycle source includes subscription/VM preflight, runner-readiness checks, time-window controls and cleanup. A runtime review on 17 October found a blocked VM-start attempt. Successful later workflow conclusions can include skipped delivery branches. They must not be counted as proof that a message was delivered. Historical infrastructure deployment remains valid evidence of the earlier deployment.

The integration uses a linked WhatsApp Business account through the browser client. Upstream client changes, session expiry or account restrictions remain dependencies. The [library's own documentation](https://github.com/wwebjs/whatsapp-web.js) identifies it as an unofficial integration; its [authentication guide](https://wwebjs.dev/guide/creating-your-bot/authentication.html) explains persistent LocalAuth storage. No independent transport-encryption assessment was performed.

## 4. Deployment and operational responsibility

The reviewed manual infrastructure workflow requires an explicit cost acknowledgement, verifies the Azure target and SKU, runs a Bicep what-if, then deploys the VM and network. This is an operator gate, not evidence of a second-person approval process.

The delivery workflow starts or checks the VM and attempts deallocation in its cleanup path. The current cleanup code also checks the resulting power state. Azure distinguishes a stopped VM from a deallocated VM; other resources can continue costing money after compute is deallocated. See [VM states and billing](https://learn.microsoft.com/en-us/azure/virtual-machines/states-billing). No savings percentage or zero-cost operation is claimed.

The inspected CI job parses cloud-init YAML, checks bootstrap shell syntax and compiles Bicep. Those checks establish syntax/build results, not live security posture, successful disaster recovery or browser-session validity.

## 5. Next engineering increments

These are review recommendations, not completed controls.

| Priority | Increment | Acceptance evidence |
|---|---|---|
| First | Re-establish and verify end-to-end runtime readiness when infrastructure access is available. | Read-only preflight, a controlled verification run, destination/session checks and verified cleanup; no resend of an already-published edition. |
| First | Separate deployment permissions from routine start/inspect/deallocate permissions; review workflow trust and pin dependencies. | Effective-role export, allowed/denied operation checks and an approved workflow change. |
| Next | Specify an explicit outbound design and recovery procedure for the persistent state. | Dependency inventory, costed egress decision, isolated restore exercise and a session-revocation/re-pairing runbook. |
| Next | Add appropriate central telemetry, security monitoring and an independent cost/cleanup alert. | A deliberately induced failure produces an actionable alert with an owner and response procedure. |

Before offering this architecture for another organisation, assess the messaging transport, data handling, hosting requirements and support expectations for that engagement. A single-workload implementation is not automatically a reusable enterprise service.

## 6. Relationship to Azure security skills

| Area from Azure security training | Evidence in this component | Remaining boundary |
|---|---|---|
| Identity and access | OIDC login, service-principal bootstrap, intended resource-group scope and VM identity configuration. | Effective-permission audit, PIM/Conditional Access and managed-identity use by the app are not demonstrated here. |
| Network security | VNet, subnet NSG and private-IP NIC definition. | No restrictive egress design, firewall or comprehensive segmentation is demonstrated. |
| Compute security | Key-based SSH configuration, service-account setup and persistent-state directory controls. | Host hardening, patch compliance and restore capability need separate verification. |
| Security monitoring | Workflow checks, readiness logic and deployment records. | Boot diagnostics and CI are not Defender for Cloud or Sentinel deployment evidence. |

This is a selected implementation mapping, not a claim to cover every [AZ-500 skill objective](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/az-500) or to establish certification status.

[Back to the case study](README.md)
