# SSO and MFA Concept Notes

This document summarises identity provider concepts in a practical, governance-oriented way.

## Single Sign-On

Single Sign-On allows users to authenticate once through a trusted identity provider and access approved applications without separate passwords for every service.

Governance questions:

- Which applications use the identity provider?
- Who owns the application integration?
- Which groups or roles are mapped to the application?
- Is access reviewed periodically?
- Are sign-in events logged centrally?

## Multi-Factor Authentication

MFA reduces reliance on passwords alone by requiring an additional factor during authentication.

Governance questions:

- Which users and roles require MFA?
- Are privileged roles always covered?
- Are exceptions documented and reviewed?
- Are emergency access accounts handled separately?
- Are failed or risky sign-ins reviewed?

## Authentication standards

| Standard | Typical use | Governance focus |
|---|---|---|
| SAML | Enterprise SSO integrations | Attribute mapping, application ownership, access review |
| OIDC | Modern application sign-in | Client registration, redirect URI control, token settings |
| OAuth2 | Delegated authorisation | Consent governance, scopes, application permissions |

## Practical documentation artifacts

- application owner list
- SSO integration inventory
- group-to-application mapping
- MFA policy baseline
- exception register
- access review evidence
