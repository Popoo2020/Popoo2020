# Evidence and verification record

[Case study](../README.md) · [Engineering review](../engineering-review.md) · [Structured evidence](deployment-review.json)

This is a sanitised portfolio record prepared from the private project's source and GitHub Actions records on **17 October 2026**. It is not a third-party attestation. Private source and execution records can be discussed in an authorised, sanitised walkthrough.

## Historical deployment: 12 September 2026

The inspected deployment job reported:

| Step | Recorded result |
|---|---|
| Azure login with OIDC | Success |
| Verify Azure target | Success |
| Check requested VM SKU in region | Success |
| Bicep what-if | Success |
| Deploy VM and network | Success |
| Wait for cloud-init | Success |
| Host status command | Success |

The workflow at that deployment revision was inspected: the deployment step invokes Azure CLI's resource-group deployment command against the Bicep template. The source and selected deployment log output were also checked.

A literal, sanitised selection from the deployment output is:

```json
{
  "noPublicIp": {
    "type": "Bool",
    "value": true
  }
}
```

This value is a declared template output. It supports traceability to the template; it is not an independent live network-inspection result. The NIC definition was separately inspected for a public-IP association.

## Validation and operational boundary

A separate infrastructure CI job on **17 October 2026** recorded successful shell-syntax validation, cloud-init YAML parsing and Bicep compilation.

The runtime review also found a blocked VM-start attempt on that date. No current end-to-end WhatsApp availability, delivery rate, readership or uptime claim is made. A green workflow with skipped delivery jobs is not counted as delivery evidence.

**Evidence strength: 4/5 for the historical deployment.** Source, job steps and logs support the claim; a direct live Azure inspection and independent third-party verification were not performed. This score is not a skill rating or a hiring-success probability.

Tenant/subscription identifiers, resource identifiers, addresses, keys, session data, destination identifiers, participant information and private account details are excluded. The structured record retains source-file fingerprints and revision identifiers for traceability without publishing private repository access links.
