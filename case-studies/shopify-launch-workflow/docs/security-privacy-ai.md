# Security, GDPR and EU AI Act review

**Reviewed 20 November 2026.** This is the design record for one SKU, one destination, a synthetic paid order and AI-assisted selection of catalog copy. It maps implemented controls to evidence and assigns production decisions to the merchant and integrator. The demonstration supplies technical evidence. A particular merchant's legal basis, transfers, retention and lawful deployment require its own factual assessment.

### Data flows and boundaries

| Recipient or component | Fields and purpose | Boundary implemented here |
|---|---|---|
| AI host for catalog work | Product title and public product facts. The host selects a headline, supporting facts and a CTA. | Public copy is assembled from approved indexes. Free text stays in the internal campaign hypothesis. Finance and delivery addresses are unnecessary for this tool. Use the local CLI for commercially sensitive planning briefs. |
| Shopify Admin | Shop currency, handle, status, SKU and price for checks. The optional write creates an unpublished development-store draft. | Exact merchant host, fixed API version, scoped token, development-plan check, explicit confirmation and no redirect forwarding. An existing handle stops the optional write. |
| Supplier rate estimate | Catalog variant, quantity, country, city, postcode, optional state and currency. | CLI opt-in or explicitly enabled MCP tool. Token stays in the local environment. Use test destinations in AI clients. |
| Supplier order preparation | Separate sync variant, quantity and only the delivery fields needed by the preparer. | Raw addresses are handled transiently on the local order path. The MCP order tool accepts no address and returns a country-level route. A provider order is never submitted by this project. |
| Evidence and replay ledger | Shop, order ID, digest, state and, after a simulated shipment, carrier and tracking reference. | Addresses and raw bodies are excluded from generated evidence and SQLite. The digest, order ID or tracking reference can still permit linkage. Treat corresponding real-world data as personal data, including in backups. |

A hosted model or MCP client can see what an operator types before server-side validation. Keep customer details, private supplier contracts and tokens out of that client. The offline sample and its signing key are deliberately public test fixtures. Replace them for any separate, properly authorized integration.

### Threats and verification

| Failure | Implemented control | Evidence or remaining production work |
|---|---|---|
| Forged or altered Shopify delivery | HMAC-SHA256 over the original bytes with constant-time digest comparison before JSON parsing. Check expected topic and shop, a bounded body size and a test-order flag. | [Verifier](../launchkit/privacy.py) · [Tamper, topic and shop tests](../tests/test_privacy.py). Real ingress also needs TLS, installation binding, key rotation, queueing and monitored acknowledgements. |
| Duplicate purchase after a repeated event | SQLite transaction and per-shop/order key. Different contents for the same order stop the rehearsal. | [Concurrent and conflicting replay tests](../tests/test_workflow.py). A future live supplier needs an outbox, durable supplier ID and reconciliation after timeouts before enabling writes. |
| Overprivileged actions or token leakage | Read-only core MCP tools. No model tool can create products, confirm supplier orders or spend ad budget. Shopify writing is an explicit CLI-only action confined to a development shop. | [Development-store gates](../launchkit/staging.py) · [Write-boundary tests](../tests/test_staging.py). Production credentials belong in a merchant-controlled secret store. |
| Misleading product claims or unintended spend | The model selects factual text by index. Content is HTML-escaped. Cash limits, fees and break-even CAC use decimal arithmetic outside the model. | [Creative controls](../launchkit/creative.py) · [Regression tests](../tests/test_workflow.py). A person must verify the underlying facts and review copy, targeting and spend. |
| Order details leak into analytics or an agent | Restricted preview schema, recipient removal from evidence, no customer identifiers in campaign URLs. | [Minimization tests](../tests/test_privacy.py) · [MCP round trip](../tests/test_mcp.py). Protect real backups, host prompts, client traces and application logs separately. |

### GDPR decisions for a real pilot

| Topic | Decision and evidence to record |
|---|---|
| Roles and purpose | Screen territorial scope under Article 3, including EU establishment, offering goods or services to people in the EU, or monitoring their behaviour there where applicable. Country fields alone do not settle that assessment. Under Articles 4, 5 and 6, identify who determines purposes and means for each flow. A merchant will commonly be controller for taking and fulfilling its orders. An integrator acting on documented instructions may be a processor. Determine Shopify's, the supplier's and any model host's role by function and contract. Record the legal basis per purpose. Processing objectively necessary to fulfil a consumer order may fall under Article 6(1)(b). Advertising and analytics require their own assessment. |
| Notice, minimization and rights | Map fields to purpose and retention (Art. 5). Explain recipients, lawful basis, transfers and rights in the applicable notice (Arts. 13–14). Give a named owner for access, deletion, restriction and objections as applicable (Arts. 12 and 15–21). Keep only what remains justified, including where a legal retention duty applies. Track deletion or justified retention at each recipient. |
| Contracts and transfers | Put Article 28 terms and subprocessor controls in place where the recipient is a processor. For transfers covered by Chapter V, document the applicable mechanism, destination and supplementary assessment where needed. A European storefront or merchant registration alone does not resolve where a supplier or model host processes data. |
| Security and response | Document risk-appropriate measures, access, encryption, recovery and control testing (Arts. 25 and 32). Maintain the applicable processing records (Art. 30). For a breach, the processor notifies the controller without undue delay. The controller assesses supervisory-authority notification and, where required, acts without undue delay and where feasible within 72 hours of awareness (Art. 33). Assess communication to affected people under Art. 34. |
| Retention and impact assessment | Assign actual retention periods to drafts, order references, logs, model prompts and backups and test expiry. The local demo persists until the operator deletes the output directory. Before production, reconcile orders before deleting deduplication keys. Screen for likely high risk and complete a DPIA where Art. 35 requires one. Reassess Art. 22 if scope expands to solely automated decisions with legal or similarly significant effects on people. |

### EU AI Act decisions

| Scope | Application to this project |
|---|---|
| Intended purpose and actors | Record the model or host, versions, prompts, approved input fields, operator, reviewer and deployment channel. Identify the provider and deployer from the actual supply arrangement under Articles 2–3. Reassess if SundAI markets its own AI system or materially changes an existing one. The catalog tool proposes how to present pre-approved product facts. |
| Classification | Check Article 5 prohibitions and Article 6 with Annexes I and III against the specific use. Ordinary selection of catalog wording in this demonstration does not, on its described facts, identify a listed high-risk purpose. A new creditworthiness, recruitment, biometric or other consequential use needs its own assessment before integration. |
| AI literacy | Article 4 as amended by Regulation (EU) 2026/1744 requires providers and deployers to take context-sensitive measures supporting staff and operator AI literacy. Give the reviewer a worked exercise on unsupported claims, customer data and when to stop. Record attendance, task and review date. A specific individual proficiency level is not guaranteed by the provision. |
| Transparency | Assess the relevant actor and use under Article 50. Direct interaction with customers, provider marking of synthetic outputs, deepfakes and public-interest text have different triggers and exceptions. This fixture has an internal merchandising assistant and human product approval. Check the host's obligations and any disclosure at publication if the output or channel changes. |
| Human decision and monitoring | Assign an owner to approve copy and the spend cap. Save the approved input facts and choice version, recheck after model changes and sample for misleading claims. This is a practical control for the stated use. A test run is not a legal conformity assessment. |

### Release record for the merchant

Before a production pilot, record the controller and operator, countries and recipients, legal bases, contract and transfer decisions, data fields and retention, AI purpose/classification, incident contact, approval evidence and a deletion test. Confirm payouts, landed cost, supplier sample, dispatch origin, returns and product requirements separately. Keep private contracts, customer orders and operational evidence in the merchant's controlled workspace.

**Primary references**

- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) · [EDPB international transfers](https://www.edpb.europa.eu/sme/be-compliant/international-data-transfers_en) · [EDPB breach guidance](https://www.edpb.europa.eu/sme/assess-the-risks/data-breaches_en)
- [EU AI Act, consolidated 27 July 2026](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng) · [Amending Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng) · [European Commission Article 50 FAQ](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act)
- [Shopify webhook verification](https://shopify.dev/docs/apps/build/webhooks/verify-deliveries) · [Shopify Payments supported countries and merchant eligibility](https://help.shopify.com/en/manual/payments/shopify-payments/supported-countries)
