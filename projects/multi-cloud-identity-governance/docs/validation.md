# Validation record

Reviewed on **26 November 2026**. The current implementation was checked on Python **3.12.14** using synthetic data. No Azure tenant, AWS account or Google Cloud project was accessed. Runtime dependencies are limited to Python's standard library; Ruff **0.14.14** is a development check.

## Observed local result

**87 tests passed** across five areas: provider input contracts, import coverage and identity mapping, adversarial authorization/time boundaries, workforce acceptance cases and evidence/CLI behaviour. Ruff lint and formatting checks passed. Test counts describe the suite, not independent features or a security certification.

```bash
python -m unittest discover -s tests -v
python -m ruff check .
python -m ruff format --check .
python -m identity_governance demo --output build/review
python -m identity_governance verify --bundle build/review/mover
python -m identity_governance verify --bundle build/review/failed-removal
```

## Acceptance outcomes

| Case | Observed model outcome |
|---|---|
| Approved mover | Three removals, three grants, staff access retained; target reached |
| Failed AWS removal | Two removals completed, one failed; all three grants blocked; partial outcome reported |
| Missing approval | Three removals completed; all three grants blocked |
| Joiner | Four approved role assignments added |
| Leaver | Identity disabled locally and four catalogued assignments removed |
| Contractor expiry | Identity disabled locally and two assignments removed |
| Periodic access review | Three obsolete assignments removed; missing finance access reported without auto-granting |

## Changes found through review

Adversarial review identified and corrected contract expiry between plan and execution, including no-op reviews; accidental refresh of observation timestamps during simulation; boolean/float schema versions; ignored security fields; non-finite JSON numbers; and one person occupying both approval roles. Regression tests also exercise rehashed forged plans, replayed/expired/denied approvals, unsupported groups/conditions, empty AWS queries, source identity mismatch and evidence modification.

The importer-to-planner test uses provider-shaped exports, validates all declared catalogue queries and reproduces the mover's six proposed operations. It does not establish that an actual cloud API was called successfully.

## Reproducible artifacts

The [successful mover](../examples/output/mover/report.md) and [failed removal](../examples/output/failed-removal/report.md) bundles are generated from the checked-in scenario. The workflow regenerates both and compares their bytes, so changes to decisions or evidence must be reviewed alongside code changes. Paths printed in `summary.json` depend on the chosen output directory; that index is not part of the committed bundles.

Evidence verification is intentionally narrower than outcome success. A truthful report of a failed removal should still pass integrity verification. The unsigned manifest is not an independent attestation.

## Continuous integration

The [portfolio workflow](https://github.com/Popoo2020/Popoo2020/actions/workflows/multi-cloud-identity-governance.yml) runs this project's tests, demonstration, evidence comparison and Ruff checks on Python 3.11 and 3.12. Its live GitHub result is the source of truth for remote execution; the local observations above must not be substituted for a successful remote run.

The project-local `.github/workflows/ci.yml` contains the equivalent configuration for extraction into a separate repository. In the current portfolio layout, only the workflow at the parent repository's root is active.
