# Selected implementation patterns

[Case study](README.md) · [Engineering decisions](engineering-review.md) · [Evidence](evidence/README.md)

This page presents deliberately limited examples. It excludes deployment coordinates, exact permission bindings, host paths, session internals and operational commands. It is not a deployable copy of the private application.

## Declarative Azure configuration

These selected properties appear in the reviewed Bicep definition, at their respective resource-property locations:

```bicep
// VM identity configuration:
identity: {
  type: 'SystemAssigned'
}

// Within the Linux configuration:
disablePasswordAuthentication: true
```

The identity declaration is evidence of configuration, not evidence that the application uses that identity to retrieve secrets. The complete reviewed template also defines the VM's networking.

## Keep credentials outside application source

The workflow supplies API credentials from GitHub Actions Secrets. The following is a generalised illustration of that pattern; the variable names are placeholders, not copied live configuration:

```yaml
env:
  MODEL_API_KEY: ${{ secrets.MODEL_API_KEY }}
```

Azure deployment uses OIDC federation. WhatsApp authentication uses separately persisted linked-device session state. No credential values or authentication-state files are included here.

## Reconcile an uncertain outcome

The following explanatory pseudocode describes the reviewed delivery logic. It is not an executable replacement:

```text
validate the confirmed edition and approved destination
if delivery is already confirmed: stop
if an earlier attempt is unresolved: reconcile its outcome
persist a pending attempt before invoking transport
send at most once in this invocation
confirm the matching outcome or retain the pending state
```

This is a duplicate-risk control for an external service. The implementation does not claim a universal exactly-once guarantee.

A technical interview can cover the design and synthetic examples without exposing recipient information, live sessions or administrative access.

[Review the validation boundaries](engineering-review.md)
