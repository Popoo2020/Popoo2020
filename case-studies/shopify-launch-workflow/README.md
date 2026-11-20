# Shopify launch workflow with supplier fulfilment and AI-assisted merchandising

A merchant has a product, a launch budget and an overseas customer in mind. Can one order pay for shipping, payment fees, returns and customer acquisition? Can the supplier receive the right SKU exactly once if Shopify delivers the same event twice? This project answers both questions before the merchant commits advertising spend.

**Read the sample decisions:** [EUR 1,000 budget](examples/results/ready.md) · [EUR 450 budget](examples/results/hold.md). **Inspect the controls:** [security, GDPR and EU AI Act](docs/security-privacy-ai.md) · [merchant pilot and market evidence](docs/merchant-pilot.md).

Starting with an empty store? Follow the [merchant handover from account setup to the first delivery](docs/store-handover.md). It identifies the configuration owned by the merchant, the evidence the software produces and the checks to repeat with an actual supplier.

### The worked example

A fictional Danish company wants to sell one paper print in Germany for EUR 39.00. Its simulated supplier dispatches within Germany. The inputs include the company's registration country, destination, currency, supplier variant, quoted freight and delivery time, merchant experience, planned marketing cost and cash reserved for the first orders.

| What the merchant learns | Result under the sample assumptions |
|---|---:|
| Product and outbound shipping | EUR 16.50 |
| Payment fee after rounding | EUR 1.28 |
| Contribution available for customer acquisition, after tax and returns allowances | EUR 13.52 |
| Contribution per order after a planned EUR 8 acquisition cost | EUR 5.52 |
| Launch cash committed, including a ten-order supplier float | EUR 670.00 |
| Headroom on the EUR 1,000 budget | EUR 330.00 |

At a EUR 450 cash budget and EUR 15 acquisition cost, the same product has a EUR 220 cash shortfall and loses EUR 1.48 per order after acquisition. The workflow issues a hold with corrective actions and withholds the catalog and campaign artifacts. These are illustrative assumptions. Commercial profit requires actual order, refund, tax, overhead and acquisition data.

### Reproduce it

From the repository root, with Python 3.12:

```bash
cd case-studies/shopify-launch-workflow
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m launchkit rehearse --out out/ready
python -m unittest discover -s tests -v
```

Open `out/ready/merchant-report.md`. The other outputs are a Shopify draft-product CSV, a GraphQL draft request, a capped campaign brief with a tagged product link, a minimized order rehearsal and a local replay ledger. All inputs for this run are bundled. The run uses signed synthetic bytes, no merchant credentials and no network calls. Each output directory is new. An invalid fixture leaves no partial bundle. Run the second case with `python -m launchkit build --brief examples/hold-brief.json --out out/hold`. Exit code 2 means the report was generated and a decision gate stopped staging.

### Follow one order through the implementation

1. [Assess the brief](launchkit/spec.py). Bind shipping to the SKU, currency, origin, destination and validity date. Check the operator's recorded payout and tax/returns reviews against the company and market. Estimate unit contribution and startup cash separately.
2. [Prepare the product and campaign](launchkit/artifacts.py). An AI client can choose which approved product facts to emphasize. Public text is rendered only from those facts. The campaign hypothesis stays outside the product description. The offline example uses a saved choice. A model is not needed to reproduce it.
3. [Check Shopify](launchkit/staging.py). Export the draft CSV or use the optional development-store command. Check the handle, draft status, SKU, price and shop currency. The [GraphQL read](launchkit/audit.graphql) and [draft mutation](launchkit/stage.graphql) target Admin API 2026-07.
4. [Check the supplier](launchkit/providers.py). The Printful adapter sends a catalog variant to the rates endpoint. The order draft uses a separate, preconfigured store sync variant tied to the print asset. The merchant must verify that mapping and the actual dispatch lane with the supplier.
5. [Rehearse delivery](launchkit/privacy.py). Verify the signature on the captured Shopify body before parsing it. [Stage a paid test order](launchkit/orders.py), replay it and record a simulated shipment. SQLite transactions produce one draft decision for duplicate deliveries, including concurrent deliveries. Conflicting replays require reconciliation. Printful receives no order in the rehearsal.

### Connect tools

| Entry point | Effect and permissions |
|---|---|
| `python -m launchkit.mcp_server` | Official MCP Python SDK over stdio. Exposes `evaluate_store`, `preview_merchandising`, `assess_supplier_rates`, `preview_supplier_order` and the `plan_catalog_copy` prompt. The last order tool accepts a synthetic order ID, test flag, SKU and quantity. Its schema rejects recipient details. |
| `python -m launchkit.mcp_server --allow-live-rate` | Adds one Printful rate-estimate tool using an operator-provided `PRINTFUL_TOKEN`. Use a sample city and postcode. A quote does not place an order. |
| `python -m launchkit printful-rate --brief my-brief.json --city Berlin --postal 10115` | Same rate adapter via CLI. Supply a store-scoped Printful token and an actual catalog variant. The quote is an input to review before updating the brief. |
| `python -m launchkit shopify-readback --brief my-brief.json` | Reads from the exact `.myshopify.com` host in the brief, using `SHOPIFY_ADMIN_TOKEN` with `read_products`. |
| `python -m launchkit stage-dev-draft --brief my-brief.json --copy my-choice.json --confirm-shop YOUR-DEV-SHOP.myshopify.com` | Explicit opt-in to create one unpublished draft. Requires a current quote, the exact confirmed store, an API-reported partner development plan, matching currency, a free handle and product read/write access. Existing products are left untouched. After an ambiguous response, read the store before trying again. |

To connect a desktop MCP host, set its command to the absolute virtual-environment Python, args to `["-m", "launchkit.mcp_server"]`, and its working directory to this project. Alternatively launch that command from the project directory. For creative work, give the host approved public catalog facts, request the merchandising prompt, preview its structured choice, and save the reviewed choice to use with `--copy`. The local MCP server is separate from Shopify's own Shop MCP. Customer checkout, advertising spend, supplier confirmation and a public webhook receiver are outside this reference.

### What the evidence establishes

Eric Ariel Rimón reports setting up Shopify store infrastructure on several occasions during the previous year. Dated working materials from October–November 2026 support supplier evaluation, landed-cost modelling, market selection and a check of catalog access. One recorded catalog check ended before product import. This public implementation was built separately from those merchants' original systems. Inputs, identifiers, addresses, costs and events are synthetic. Historical store counts, merchant receipts, revenue and conversion rates are not claimed as verified results.

All 24 test methods passed both in the working environment and in a newly installed Python 3.12 environment. The regression suite uses an actual MCP client and stdio server, mocked HTTP transports, and a file-backed SQLite ledger. The two GraphQL operations were also validated against Shopify's 2026-07 schema. The generated product variables were checked against the official `ProductSetInput` type. Live merchant credentials, provider acceptance of a paid order and end-customer delivery are separate pilot acceptance tests.

[Shopify product CSV](https://help.shopify.com/en/manual/products/import-export/using-csv) · [Admin productSet](https://shopify.dev/docs/api/admin-graphql/2026-07/mutations/productSet) · [Shopify API versioning](https://shopify.dev/docs/api/usage/versioning) · [Printful API](https://developers.printful.com/docs/) · [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
