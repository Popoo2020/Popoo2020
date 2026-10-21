# Evidence register, business outcomes and reviewer guide

The historical case and the new 2026 demonstration have **different evidence bases**. Scores below are evidence strength, **not probabilities of hiring success**.

| Claim | Evidence basis | Strength (1–5) | Gap |
|---|---|---:|---|
| Ariel's Pizza operated across three locations | Founder/operator account | 3 | Historical business records not independently inspected here |
| Original Python/OpenAI assistant integrated ordering, Trello, Sheets and WhatsApp | Builder's first-hand description | 3 | Historical source, API traces and logs not inspected |
| Manager escalation, inventory and shift tasks | Operator account | 3 | No independent historical execution receipts |
| Tool and concept transferred with May 2025 sale | Operator account | 3 | No public contract/IP schedule verified |
| New offline demo validates/routes invented events | New code, model-output contract, tests and reproducible JSON output | 4 | Demonstration only, not historical software or live integration |
| Original system's security configuration | No independent records | 1 | Not established by the new sample |
| Quantified time savings, ROI, revenue, staff/customer satisfaction | No measured baseline/outcomes | 1 | Do not make numerical improvement claims |

**Scale and practical result:** the operator reports deploying a task-support workflow for a business operating across three locations and transferring the tool/concept on sale. The implementation story illustrates requirements discovery, workflow design, multi-tool coordination, staff adoption and human oversight. No reduction in staffing time, waste, costs or complaints has been measured or independently verified in this case.

## Five-minute reviewer walkthrough

1. Read the [case-study scope](README.md) and [historical versus new architecture](architecture.md).
2. Run the new code locally from this directory: `python -m demo.scenarios`.
3. Compare the JSON with [the labelled synthetic sample](demo/sample-output.json).
4. Run `python -m unittest discover -s demo/tests -v`; inspect rejection of personal fields, role bypass, conflicting duplicates and manager-review rules.
5. Read the [security limitations](security-and-oversight.md) and inspect [CI](../../.github/workflows/ariels-pizza-demo.yml).

The new demonstration contains **no** real external connectors. Passing its tests verifies only the code in this repository, not the original product's availability, security, API behaviour or impact.

## Historical evidence that might improve confidence

If lawfully retained **and** disclosure is authorised by the current IP owner, suitably redacted dated architecture notes, screenshots, correspondence or contractual excerpts could improve the historical evidence. **No such materials are included or claimed to have been inspected.** Do not upload customer/employee conversations, absence information, financial records, secrets or transferred proprietary code.

## CV-safe positioning

> Built an AI-assisted operations workflow for a three-location food business, connecting ordering information and team coordination with manager-reviewed tasks. The original implementation is private/transferred; a separate 2026 offline Python demonstration illustrates validation, decision routing and human oversight.

Avoid unsupported claims such as “saved 30% staff time”, “automatically processed all orders”, “production-certified security” or “original code publicly available”.

[Case study](README.md) · [Demo instructions](demo/README.md) · [Career evidence guide](../../career-portfolio/evidence.md)
