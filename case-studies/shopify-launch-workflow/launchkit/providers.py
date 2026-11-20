"""Provider pricing, version checks and catalog audits. Writes are gated by staging.py."""

from decimal import Decimal
from pathlib import Path

import httpx

from .spec import Brief, money

VERSION = "2026-07"
QUERY = Path(__file__).with_name("audit.graphql").read_text(encoding="utf-8")


def audit_draft(brief: Brief, response: dict) -> dict:
    if response.get("errors") or not isinstance(response.get("data"), dict):
        raise ValueError("Shopify returned GraphQL errors or no data")
    data = response["data"]
    try:
        shop_currency = data["shop"]["currencyCode"]
        nodes = data["products"]["nodes"]
        matches = [p for p in nodes if p["handle"] == brief.product.handle]
        if len(matches) != 1:
            return {"matches": False, "issues": ["expected_one_matching_product"]}
        product = matches[0]
        variants = product["variants"]["nodes"]
        issues = []
        if shop_currency != brief.currency:
            issues.append("shop_currency")
        if product["status"] != "DRAFT":
            issues.append("product_status")
        if len(variants) != 1 or variants[0]["sku"] != brief.product.sku:
            issues.append("variant_or_sku")
        elif Decimal(variants[0]["price"]) != brief.product.sale_price:
            issues.append("price")
    except (KeyError, TypeError, ArithmeticError) as exc:
        raise ValueError("unexpected Shopify response shape") from exc
    return {"matches": not issues, "issues": issues}


def shopify_call(brief: Brief, token: str, client: httpx.Client, payload: dict) -> dict:
    # The shop domain is validated by Brief. Redirects stay disabled.
    url = f"https://{brief.shop}/admin/api/{VERSION}/graphql.json"
    response = client.post(
        url, headers={"X-Shopify-Access-Token": token}, json=payload, follow_redirects=False
    )
    response.raise_for_status()
    reported = response.headers.get("X-Shopify-API-Version")
    if reported and reported != VERSION:
        raise ValueError(
            f"Shopify served {reported}. Review the pinned contract before continuing."
        )
    data = response.json()
    if data.get("errors") or not isinstance(data.get("data"), dict):
        raise ValueError("Shopify returned GraphQL errors or no data")
    return data


def read_shopify(brief: Brief, token: str, client: httpx.Client) -> dict:
    payload = {"query": QUERY, "variables": {"search": "handle:" + brief.product.handle}}
    return audit_draft(brief, shopify_call(brief, token, client, payload))


def read_printful(
    brief: Brief, token: str, postal: str, city: str, state: str | None, client: httpx.Client
) -> dict:
    recipient = {"country_code": brief.market, "zip": postal, "city": city}
    if state:
        recipient["state_code"] = state
    response = client.post(
        "https://api.printful.com/shipping/rates",
        headers={"Authorization": "Bearer " + token},
        json={
            "recipient": recipient,
            "items": [{"variant_id": brief.supplier.catalog_variant_id, "quantity": 1}],
            "currency": brief.currency,
        },
        follow_redirects=False,
    )
    response.raise_for_status()
    return select_rate(brief, response.json())


def select_rate(brief: Brief, response: dict) -> dict:
    if response.get("code") != 200 or not isinstance(response.get("result"), list):
        raise ValueError("Printful did not return a rates list")
    options = []
    for offer in response["result"]:
        if offer.get("currency") != brief.currency:
            continue
        days = offer.get("maxDeliveryDays")
        if type(days) is not int or not 0 < days <= brief.marketing.max_delivery_days:
            continue
        try:
            rate = Decimal(str(offer["rate"]))
        except (KeyError, ValueError, ArithmeticError):
            continue
        if rate.is_finite() and rate >= 0 and offer.get("id"):
            options.append((rate, days, str(offer["id"])))
    if not options:
        raise ValueError("no quoted service fits the currency and delivery limit")
    rate, days, service = min(options)
    return {
        "market": brief.market,
        "currency": brief.currency,
        "per_unit": str(money(rate)),
        "max_days": days,
        "service": service,
    }
