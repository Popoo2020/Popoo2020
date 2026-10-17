# Operating Controls and Measurement Scope

[Azure case study](README.md) · [Engineering decisions](engineering-review.md) · [Evidence](evidence/README.md)

**Review:** October 2026. This page separates inspected source configuration from operator estimates and measured outcomes. The source review was read-only; it did not deploy the application, run production jobs or audit an Azure bill.

## Routine human effort

The operator estimates **approximately one minute of routine human input per edition**.

No timed sample, observation period, manual-work baseline or statistical average accompanies that estimate. It should not be restated as a measured percentage reduction, a guarantee for every edition or the total effort required for maintenance and incident recovery.

## Resource controls found in source

| Area | Inspected implementation | Scope of the claim |
|---|---|---|
| Model output | Explicit output-token limits on model calls. | Bounds selected request outputs; not a total account-spend ceiling. |
| Generation and review | Deadlines, request timeouts and bounded attempts. | Limits individual workflow work and retries; execution outcomes still need monitoring. |
| Draft evaluation | A bounded number of independent draft evaluations and comparison reporting. | Repeatable quality checking; not evidence of autonomous model learning. |
| Input workload | Bounds on candidate enrichment and evaluation batch size. | Limits work in the reviewed processing paths; not a universal internet-traffic cap. |
| Artifact storage | Finite retention for uploaded workflow artifacts. | Applies to those artifacts; not a tenant-wide Azure storage quota. |
| Azure compute | Workflow time limits and a VM-deallocation cleanup path. | A compute-lifecycle control; not proof of cleanup success after every possible failure. |

Task-appropriate model selection and fallback configuration also appear in the implementation. A model being lightweight or a task using less reasoning does not by itself establish the lowest monetary cost.

Exact limits, account configuration and operational recovery details are intentionally excluded from this public page.

## Quality refinement

Source filters, editorial checks, publication gating and repeatable draft evaluations support iterative workflow refinement. These mechanisms are described as **quality checks and iterative refinement**.

They do not establish:
- a benchmarked factual-accuracy percentage;
- ongoing training or modification of model weights;
- improvement on every run;
- a delivery-success rate.

Any published quality metric should identify what was assessed, the sample and period, the acceptance rule and who performed the assessment. Model-generated ratings and independent factual evaluation are different evidence.

## Cost language

The supported claim is **cost-conscious implementation with bounded resource use in specific workflow paths**. No monthly cost, minimum possible cost or measured savings figure is asserted.

Microsoft distinguishes a stopped-but-allocated VM from a deallocated VM. Disks and some networking resources can continue to incur charges after compute is deallocated. See [Azure VM states and billing](https://learn.microsoft.com/en-us/azure/virtual-machines/states-billing).

## Evidence assessment

- **4/5 — presence of the listed controls in source:** configuration and implementation paths were inspected; this was not a new runtime or billing audit.
- **3/5 — approximately one minute of routine human input:** direct operator estimate, without a timed sample.
- Quantified quality, savings and ongoing availability require their own measurement evidence.

[Return to the technical case study](README.md)
