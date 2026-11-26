# Portfolio benchmark: identity and cloud security

Reviewed on **26 November 2026**. This benchmark informed the presentation and review criteria for Multi-Cloud Identity Governance. It compares three individual GitHub profiles and three community projects. It is not a ranking of people, a security audit, or evidence that a particular README causes hiring success.

## What was checked

The profile pages, actual README files, repository metadata, and selected contribution/security policies were read from GitHub. Repository stars, forks, and push timestamps below came from the GitHub REST API through the GitHub connector. Follower counts came from public GitHub profile pages and may reflect cached snapshots; rounded displays are explicitly identified. These are dated observations, not live counters. No external project was installed or executed for this review.

Stars indicate visible interest; forks indicate repository copies. Neither establishes production adoption, endorsement, security quality, or an individual's contribution. An organization's project popularity must not be presented as a maintainer's personal popularity.

## Comparison

| Reference | Verified interest and activity snapshot | What was actually observed | Lesson for this portfolio |
| --- | --- | --- | --- |
| [Merill Fernando's individual profile](https://github.com/merill) and [profile README](https://github.com/merill/merill/blob/main/README.md) | Profile displayed **946 followers**. Profile repository last push: **2026-11-13 20:15:43 UTC**. Profile-repository stars are not used as a reputation measure. | A short statement of practical value, a featured project, a table pairing each tool with its purpose, direct links to work, and recent writing. The page identifies its relationship to Maester. Audience/traffic claims in the author's prose were not independently verified and are not repeated here. | Explain who the work helps and show a few inspectable deliverables. Keep the personal profile readable and link to the detailed project evidence. |
| [Nathan McNulty's individual profile](https://github.com/nathanmcnulty) and [profile README](https://github.com/nathanmcnulty/nathanmcnulty/blob/main/README.md) | Profile displayed **286 followers**. Profile repository last push: **2026-10-22 10:08:43 UTC**. | A first-person career story names specific platforms; a Requests section invites script ideas and fixes. Pinned repositories include defender-reporting and azd-maester. Career claims are the author's account, not independently checked here. | Connect Ariel's business background to his current technical work, show focused pinned examples, and invite concrete feedback. |
| [Dirk-jan's individual profile](https://github.com/dirkjanm) and pinned [ROADtools README](https://github.com/dirkjanm/ROADtools/blob/master/README.md) | Profile displayed **2.5k followers (rounded)**; exact total not retrieved. ROADtools separately had **2,780 stars; 402 forks**, last push **2026-11-20 13:43:26 UTC**. | A sparse profile foregrounds six focused pinned tools. ROADtools explains its library, exploration, and authentication components separately, with installation and usage links. | Let inspectable projects establish specialization. Give each pin a clear purpose and explain component boundaries instead of relying on a broad expert title. |
| [Maester](https://github.com/maester365/maester) — organization/community project | **1,201 stars; 303 forks.** Last push: **2026-11-26 05:42:08 UTC**. | The README gives installation/run commands, version and migration constraints, CI links, report formats, and a way to add checks. Its native test design pairs an ID-bearing test file with a description/remediation file. Its security policy defines reporting and scope. | Give controls stable IDs and explain their rationale, evidence, and remediation. Show reproducible results and document compatibility. Link to CI without claiming a pass that has not been observed. |
| [Prowler](https://github.com/prowler-cloud/prowler) — organization/community project | **15,336 stars; 2,527 forks.** Last push: **2026-11-26 11:21:30 UTC**. | The README combines business/security purpose, CLI and dashboard examples, output illustrations, a provider capability table, installation routes, and an architecture diagram. It distinguishes support/interface coverage by provider. | Make capabilities easy to compare across clouds. Show an output and a compact architecture before asking readers to inspect code. Separate supported behavior from planned coverage. |
| [Cartography](https://github.com/cartography-cncf/cartography) — organization/community project | **4,205 stars; 619 forks.** Last push: **2026-11-25 23:43:55 UTC**. | The README opens with practical access/infrastructure questions, then an install-to-query walkthrough and platform scope. Its contribution guide requires real-provider testing and sanitized evidence for connector changes; mocked tests alone do not establish live API functionality. | Lead with the questions the project answers. Provide a complete input-to-result example and disclose the validation level of each adapter. Keep cloud integration claims proportional to evidence. |

Merill's profile and Maester are related examples, not independent endorsements. The projects are substantially more mature than a new portfolio repository; their scale and adoption claims are not claims about this project.

## Recommendations applied as review criteria

These are design and publication criteria for this repository. They do not, by themselves, certify that a feature is implemented or tested. The implementation, generated outputs, and CI results determine completion.

| Area | Concrete application | Evidence needed before claiming completion |
| --- | --- | --- |
| Business-first README | Open with workforce-access questions: which residual assignments remain after a role move, which planned grants lack valid approvals, and what evidence a reviewer can inspect. Identify the intended security, platform, and governance users. | Every advertised question has a working rule/example or is explicitly marked as future work. |
| Runnable example | Put a credential-free synthetic example near the top. Include prerequisites, exact commands, the expected output location, and one understandable finding. | Run the documented commands from a clean checkout; compare the result with the committed sample. |
| Evidence traceability | Attach stable control IDs, source-record references, an explanation, and a remediation suggestion to findings. Distinguish observed facts from review assumptions. | A reviewer can trace a sample finding back to the input and understand what would change the outcome. |
| Cloud adapter matrix | Give each provider separate columns for input format, normalization, fixture coverage, live collection, and real-environment validation. | Populate each cell from implemented code and recorded tests. Importing a saved export does not establish live collection. |
| Tests and CI | Exercise malformed/missing data, identity linkage, approval binding, expiry boundaries, control failures, and predictable report output. | Tests prove meaningful behavior, including negative cases. Report local verification separately from a successful remote workflow. |
| Architecture and threat model | Diagram the input, normalization, rules, and report boundary. Document untrusted exports, secrets/personal data, report injection, and the limits of any assessment. | Risks and mitigations correspond to code or explicit operational constraints; disclose remaining limitations. |
| Decision records | Record why the first version uses its chosen input approach, identity model, control mappings, and dependencies. Explain trade-offs and when to revisit them. | Each decision matches the implemented system. Decision records are our design choice, not a claimed feature of every benchmarked project. |
| Governance positioning | Describe control mappings as assessment support. Explain the evidence a human reviewer still needs and the boundaries of legal/standard interpretation. | No claim that a passing technical check certifies an organization, proves legal compliance, or replaces an audit. |
| Profile README | State Ariel's practical focus, link this project and its demo/evidence, and describe actual responsibilities and completed work. | Claims match inspectable work. Certifications and experience are included only when verified or clearly attributed to the author's account. |
| Contribution and security policy | Provide a small reproducible-bug template and an appropriate reporting route. | The route exists, and no response-time promise or support commitment is invented. |

For live collection added later, use Cartography's evidence standard as a useful benchmark: test in an authorized provider environment and retain sanitized run evidence. Unit tests remain valuable, but must not be relabeled as a successful production integration.

## What should not be copied

The useful patterns are clarity, reproducibility, traceability, and honest scope. This repository does not copy another project's code, branding, logos, testimonials, counters, contributor lists, or claims of adoption. It does not reuse maintainer biographies as claims about its author. An attractive profile is a way to make evidence accessible; it is not evidence of seniority on its own.

## Source record

All sources were retrieved for this review on 26 November 2026. Branch URLs can change after that date. The README blob hashes identify the content read; they are Git blob IDs, not commit IDs.

| README | Blob SHA read |
| --- | --- |
| [merill/merill](https://github.com/merill/merill/blob/main/README.md) | cfdd3c2a8b8974c0eec29b1c5828c773658c0e63 |
| [nathanmcnulty/nathanmcnulty](https://github.com/nathanmcnulty/nathanmcnulty/blob/main/README.md) | 6521b10e294b9d3d42aad2b0c74a63b46d20ada4 |
| [dirkjanm/ROADtools](https://github.com/dirkjanm/ROADtools/blob/master/README.md) | 9959fb29be091a9f20994185b4141bbc778ec0e1 |
| [maester365/maester](https://github.com/maester365/maester/blob/main/README.md) | ae436dcdadbb51e3e64f57dba0d4a1558ad536d6 |
| [prowler-cloud/prowler](https://github.com/prowler-cloud/prowler/blob/master/README.md) | 70d14c9567b556c834240f14dbddf7bd7b904a6f |
| [cartography-cncf/cartography](https://github.com/cartography-cncf/cartography/blob/master/README.md) | 0ce49c9f3494ef62af6c1281b0c27b97599f03c6 |

Additional primary sources:

- Repository metadata: [Merill profile repository](https://api.github.com/repos/merill/merill), [Maester](https://api.github.com/repos/maester365/maester), [Prowler](https://api.github.com/repos/prowler-cloud/prowler), [Cartography](https://api.github.com/repos/cartography-cncf/cartography).
- Additional individual-owned repositories: [Nathan's profile repository](https://api.github.com/repos/nathanmcnulty/nathanmcnulty), [Dirk-jan's ROADtools](https://api.github.com/repos/dirkjanm/ROADtools).
- [Cartography contribution and connector validation requirements](https://github.com/cartography-cncf/cartography/blob/master/CONTRIBUTING.md).
- [Maester security policy](https://github.com/maester365/maester/blob/main/SECURITY.md).
- [Prowler security policy](https://github.com/prowler-cloud/prowler/blob/master/SECURITY.md).

**Evidence assessment:** 4/5 for the observed files and metadata: direct primary evidence, with snapshot/cache limits and no independent audit. Recommendations are reasoned design choices; this review makes no quantified claim about their effect on recruitment or community popularity.
