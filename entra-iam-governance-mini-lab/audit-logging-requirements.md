# IAM Audit Logging Requirements

This document lists practical logging expectations for identity and access governance.

## Events to log

- Successful sign-ins
- Failed sign-ins
- MFA challenges and failures
- Privileged role assignments
- Group membership changes
- Application consent events
- Conditional access policy changes
- Password or credential reset events
- Service account changes
- Emergency access account usage

## Evidence expectations

| Event type | Why it matters | Review frequency |
|---|---|---|
| Privileged role assignment | Shows who received elevated rights | Monthly |
| Failed sign-ins | May indicate user issues or risk | Weekly or event-driven |
| Conditional access changes | Sensitive policy change | After each change |
| Application consent | Can affect data access | Monthly |
| Emergency account use | High-risk exception path | Immediately after use |

## Governance notes

- Logs should have an owner.
- Retention expectations should be defined.
- Access to logs should be limited.
- Critical identity events should be reviewable.
- Evidence should support audit, incident response and operational improvement.
