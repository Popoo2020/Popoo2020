# Control mapping and evidence limits

Reviewed: **26 November 2026**. This is a project-authored, limited cross-reference, not an audit conclusion, Statement of Applicability or compliance certificate. Control descriptions below are paraphrases; licensed ISO text is not reproduced. See [standards and legal sources](sources.md#standards-and-law).

## Project control identifiers

These IDs belong to this project; they are not ISO or NIS2 identifiers. Each generated `assessment.json` and report includes a finding, evidence paths and a reviewer action.

| Project ID | Question answered | Main evidence |
|---|---|---|
| IG-01 | Are the subject, policy and observation scope explicitly linked? | Plan and before snapshot; import provenance when used |
| IG-02 | Which catalogued assignments remain unjustified or missing? | Before/after snapshots and reconciliation result |
| IG-03 | Do new grants have two distinct, valid approvals bound to this plan? | Approval records and operation decisions |
| IG-04 | Does the resulting model violate a configured separation-of-duties rule? | Policy-derived plan and final conflict check |
| IG-05 | Are departure or expiry actions completed within the local model? | Disable/removal outcomes and after snapshot |
| IG-06 | Can a reviewer follow the decision trail and check local integrity? | Audit chain, file manifest and verification command |

## ISO/IEC 27001:2022

The candidate Annex A references help explain why the workflow matters. Selection and adequacy depend on an organization's scope, risk assessment, policies and implementation; ISO/IEC 27002 supplies associated guidance.

| Candidate reference | Demonstrated contribution | Evidence and remaining gap |
|---|---|---|
| A.5.15, A.5.16 | Connect identity lifecycle events to explicit access rules and stable identity records. | HR fixtures and desired/current state. HR legitimacy, identity proofing and inventory completeness are not verified. |
| A.5.18 | Review, approve, change and remove assigned rights as work changes or ends. | Plans, approvals and before/after snapshots. Cloud execution, downstream propagation and actual owner authentication remain unimplemented. |
| A.8.2, A.8.3 | Separate sensitive access and avoid retaining incompatible old grants during a move. | Ordered actions and failure scenarios. Local grants do not establish least privilege across every cloud permission or inherited path. |
| A.8.15 | Record decisions, outcomes and failures so a reviewer can follow a change. | `audit.jsonl` and `manifest.json`. No independent signature, protected log service or retention enforcement. |

An individual's implementer qualification and an organization's certified management system are different claims. This repository supplies neither certification nor evidence that all management-system requirements operate effectively. [ISO1–ISO3](sources.md#standards-and-law)

## NIS2 Article 21

Article 21(2)(i), concerning people, access policies and assets, is the closest connection: the lifecycle model and entitlement records support a narrow access-governance task. Article 21(2)(f), concerning assessment of measures, relates to reproducible checks and recorded failures; simulator tests are not an organization-wide effectiveness assessment. For Article 21(2)(j), MFA and secure authentication belong in the surrounding architecture, but this project neither enforces nor validates MFA. [EU1](sources.md#standards-and-law)

A European address and 180 employees do not by themselves establish NIS2 applicability. Sector, activity, size rules, exceptions and the relevant national law require assessment. The EU transposition deadline was **17 October 2024**, not an upcoming deadline. This mapping does not extend NIS2 automatically to every European or US business.

ENISA's implementation guidance offers examples of evidence and mappings for specified digital-service sectors under Implementing Regulation 2024/2690. It informs the evidence approach here; the fictional distributor is not asserted to belong to those sectors. [EU2](sources.md#standards-and-law)

## What a reviewer can conclude

The evidence can demonstrate that the local engine distinguishes approved grants, stale plans, expiry, removals and partial failure within its fixtures. It cannot establish who really approved, whether source exports were complete, whether a live cloud accepted a change, or whether existing sessions lost access.

The professional relevance is concrete: provider documentation describes authoritative identity sources, assignment lifecycles, policy conditions and revocation limitations; NIS2 addresses access governance and assessment. This supports the choice of portfolio problem. It is not evidence of job counts, junior hiring rates, consulting revenue or guaranteed market demand.
