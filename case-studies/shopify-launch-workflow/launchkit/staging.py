"""Optional create-only staging in an operator-confirmed Shopify development store."""

from datetime import date
from pathlib import Path

import httpx

from .creative import CreativeChoice, product_description, render_copy
from .providers import QUERY, audit_draft, shopify_call
from .spec import Brief, evaluate

MUTATION = Path(__file__).with_name("stage.graphql").read_text(encoding="utf-8")


def draft_request(brief: Brief, copy: dict) -> dict:
    variant = {
        "price": f"{brief.product.sale_price:.2f}",
        "inventoryItem": {"sku": brief.product.sku, "requiresShipping": True},
        "optionValues": [{"optionName": "Title", "name": "Default Title"}],
    }
    product = {
        "handle": brief.product.handle,
        "title": brief.product.title,
        "descriptionHtml": product_description(copy),
        "status": "DRAFT",
        "productOptions": [{"name": "Title", "values": [{"name": "Default Title"}]}],
        "variants": [variant],
    }
    # Omit identifiers and IDs. This request is only for a newly created product.
    return {"query": MUTATION, "variables": {"input": product}}


def stage_dev(
    brief: Brief,
    choice: CreativeChoice,
    confirmed_shop: str,
    token: str,
    client: httpx.Client,
    *,
    today: date | None = None,
) -> dict:
    if confirmed_shop != brief.shop or evaluate(brief)["decision"] != "READY_FOR_REHEARSAL":
        raise ValueError("confirm this exact shop and resolve every launch gate before staging")
    on_date = today or date.today()
    if not brief.as_of <= on_date <= brief.shipping.valid_until:
        raise ValueError("live staging requires a current brief and supplier quote")
    copy = render_copy(brief, choice)
    before = shopify_call(
        brief,
        token,
        client,
        {"query": QUERY, "variables": {"search": "handle:" + brief.product.handle}},
    )
    shop = before["data"]["shop"]
    if (
        shop["myshopifyDomain"] != brief.shop
        or not shop["plan"]["partnerDevelopment"]
        or shop["currencyCode"] != brief.currency
    ):
        raise ValueError("staging requires a matching development shop and currency")
    existing = before["data"]["products"]["nodes"]
    if existing:
        raise ValueError("a product was found; left untouched. Run shopify-readback and reconcile.")
    # Do not retry a mutation following a timeout. A subsequent attempt starts with the same handle audit.
    result = shopify_call(brief, token, client, draft_request(brief, copy))
    written = result["data"]["productSet"]
    if written["userErrors"] or not written["product"]:
        raise ValueError("Shopify declined the draft. Reconcile the handle before retrying.")
    audit = audit_draft(
        brief, {"data": {"shop": shop, "products": {"nodes": [written["product"]]}}}
    )
    if not audit["matches"]:
        raise ValueError("draft response differs from the brief; inspect the development store")
    return {"state": "DEVELOPMENT_DRAFT_CREATED", "handle": brief.product.handle, "status": "DRAFT"}
