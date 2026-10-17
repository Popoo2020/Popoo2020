# Denmark in 5 — Azure Delivery Architecture

**AI implementation, API integration, Azure infrastructure and security controls**

Denmark in 5 turns Danish news and practical information into a Hebrew briefing for Israelis in Denmark. I develop the workflow through SundAI in collaboration with Living Denmark, connecting Python and model APIs with editorial checks and distribution.

This case study focuses on my Azure delivery component: infrastructure defined in Bicep, GitHub-to-Azure authentication, a persistent messaging bridge and controlled delivery of the confirmed edition.

**Evidence:** a successful infrastructure deployment was recorded in September 2026. Source and execution records were reviewed in October 2026. Historical deployment evidence and current service availability are separate claims.

[Engineering decisions](engineering-review.md) · [Selected implementation patterns](implementation-excerpts.md) · [Evidence](evidence/README.md) · [Public disclosure scope](public-disclosure.md) · [Back to my profile](../../README.md)

## The problem and my contribution

A scheduled briefing needs more than generated text. It needs to preserve the selected edition, reach the approved destination, avoid careless retries and leave a clear outcome for the operator.

- **Build the workflow:** connect source processing, model APIs, structured outputs and publication checks.
- **Define its infrastructure:** use Bicep for an Azure VM, virtual network, subnet and network security group.
- **Separate credential paths:** use Actions Secrets for application credentials, OIDC for Azure authentication and separate persistent messaging session state.
- **Control delivery:** validate the edition artifact, maintain a delivery journal and reconcile uncertain outcomes before retrying.
- **Operate responsibly:** add readiness checks, deployment validation, documentation and a VM-deallocation cleanup path.

## How the implemented architecture fits together

This is a logical view of the implemented components. Operational identifiers, exact permission bindings, host configuration and recovery procedures are deliberately excluded.

```mermaid
flowchart TD
    subgraph GH["GitHub"]
        S["Actions Secrets"]
        G["Generation and lifecycle workflows"]
        A["Confirmed edition artifact"]
        S -. "Application credentials" .-> G
        G --> A
    end

    subgraph AZ["Azure"]
        E["Microsoft Entra federation"]
        subgraph VN["Virtual network"]
            V["Private-IP VM: delivery bridge"]
            D["Persistent messaging session and journal"]
            V <--> D
        end
    end

    G -. "OIDC exchange" .-> E
    E -. "Short-lived access token" .-> G
    G -->|"Lifecycle via Azure management API"| V
    A -->|"Validated artifact retrieval"| V
    G --> T["Telegram"]
    V -->|"Outbound WhatsApp Web session"| W["WhatsApp Business account"]
```

The bridge retrieves the confirmed artifact. The VM definition has no public IP associated with its network interface. This is not a claim that the entire environment is isolated or independently security-certified.

**Transport boundary:** the WhatsApp Business account connects through WhatsApp Web using `whatsapp-web.js`. This is a browser-based integration, not Meta's official Business Platform Cloud API.

## Separate handling of secrets and session state

| Material | Implemented approach |
|---|---|
| Model-provider and Telegram credentials | GitHub Actions Secrets, supplied to the workflow that needs them. |
| Azure deployment authentication | Entra OIDC federation; the reviewed login flow does not use a stored Azure client password. |
| Edition-artifact access | A GitHub job token with read permissions. |
| WhatsApp authentication state | Persistent session storage outside the code checkout, with filesystem access restrictions. |

These are distinct credential paths. They do not establish independent vault isolation or Azure Key Vault integration. Credential values, session files, recipient data and live configuration are excluded from this public case study.

## Value for a team

I can translate an operational need into a Python/API workflow, connect it to Azure infrastructure, explain the relevant security controls and document its operating limits. My focus is **AI Implementation & Automation**: delivering a defined component, discussing trade-offs and handing over work that colleagues can understand.

The public evidence supports the implementation and historical deployment described here. It does not claim measured business savings, continuous availability or a completed enterprise security assessment.

[Explore the engineering decisions](engineering-review.md) · [Contact Eric Ariel Rimón](mailto:eririmo@protonmail.com)
