# Selected implementation excerpts

[Case study](README.md) · [Engineering review](engineering-review.md) · [Evidence](evidence/README.md)

These excerpts explain the existing implementation. They are deliberately partial, with resource names and contextual identifiers omitted or generalised. They are not a standalone deployment package. The evidence record distinguishes the historical deployment revision from the source snapshot reviewed on 17 October 2026.

## Azure VM configuration

Selected properties from the deployed Bicep definition:

```bicep
identity: {
  type: 'SystemAssigned'
}

// Within osProfile.linuxConfiguration:
disablePasswordAuthentication: true
provisionVMAgent: true
ssh: {
  publicKeys: [
    {
      path: '/home/${adminUsername}/.ssh/authorized_keys'
      keyData: adminSshPublicKey
    }
  ]
}
```

The NIC has a dynamically assigned private IP and no public-IP association. The template creates a subnet NSG with `securityRules: []`: Azure defaults still apply. It explicitly enables `defaultOutboundAccess: true`. Neither an empty custom-rule list nor a private-IP NIC means that all traffic is denied.

## GitHub-to-Azure federation

Selected properties from the deployment workflow:

```yaml
permissions:
  id-token: write
  contents: read

# Selected job steps:
steps:
  - name: Azure login with OIDC
    uses: azure/login@v2
    with:
      client-id: ${{ secrets.AZURE_CLIENT_ID }}
      tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

These three values identify the Azure target and identity. The login flow uses federation rather than a stored Azure client password. The bootstrap's intended RBAC scope is the dedicated workload resource group. Action version tags are shown as found; immutable commit pinning is a review recommendation.

## Application secrets remain outside source

Selected environment entries from the Python briefing job:

```yaml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
```

The delivery job has a different credential path: its GitHub token reads the confirmed artifact, while LocalAuth on the VM supplies the WhatsApp linked-device session. The reviewed bridge job does not inject the model-provider keys or Telegram bot token.

## Persistent WhatsApp authentication

Selected logic from the transport implementation:

```javascript
await fs.mkdir(config.authDir, { recursive: true, mode: 0o700 });

class PreserveLocalAuth extends LocalAuth {
  async logout() {}
}

const client = new Client({
  authStrategy: new PreserveLocalAuth({
    clientId: 'denmark-in-5',
    dataPath: config.authDir,
  }),
  puppeteer,
  takeoverOnConflict: false,
});
```

The directory sits on the persistent disk outside the checkout. Preserving authentication during reconnect/cleanup avoids accidental session loss, but it makes deliberate revocation and deletion procedures important. The mode is a directory-creation setting; this excerpt does not attest existing filesystem permissions or prove encryption of the stored profile.

## Reconciliation before retry

The delivery implementation persists a pending attempt before calling the transport. After a send error, it checks for an already-accepted outgoing message rather than sending again. The full reviewed function also validates the date, target and earlier journal state.

This behaviour is represented here in explanatory pseudocode, not as an executable replacement:

```text
validate current edition and approved destination
if already confirmed: stop
if a prior attempt exists: reconcile; do not resend
persist pending attempt
send at most once in this invocation
confirm matching outgoing message and acknowledgement
record confirmation, or leave the attempt pending for reconciliation
```

[Read the limits and proposed improvements](engineering-review.md)
