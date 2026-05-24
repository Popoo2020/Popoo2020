# Conditional Access Baseline

This document provides a simple baseline for documenting conditional access expectations in a Microsoft-oriented environment.

## Baseline principles

- Require MFA for privileged roles.
- Require MFA for external access.
- Block legacy authentication where possible.
- Apply stronger controls to high-risk sign-ins.
- Use named roles and groups rather than ad hoc exceptions.
- Review exceptions regularly.

## Example policy areas

| Policy area | Purpose | Evidence example |
|---|---|---|
| MFA for administrators | Protect privileged access | Policy export, admin role list, review record |
| Legacy authentication block | Reduce exposure from older protocols | Policy setting, exception list |
| External access control | Protect access from unmanaged locations | Conditional access policy, sign-in logs |
| Device or session controls | Reduce session risk | Device compliance setting, session policy notes |
| Emergency access accounts | Maintain availability during incidents | Break-glass account procedure and review record |

## Exception handling

Every exception should include:

- business reason
- owner
- start date
- end date or review date
- compensating control
- approval record

## Review checklist

- Are privileged users covered by MFA?
- Are emergency accounts documented?
- Are exceptions still needed?
- Are high-risk sign-ins reviewed?
- Are service accounts separated from user accounts?
