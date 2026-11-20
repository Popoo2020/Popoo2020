"""Verify a captured Shopify delivery and minimize its data before local processing."""

import base64
import hashlib
import hmac
import json


def normalize_delivery(body: bytes, headers: dict, expected_shop: str, secret: bytes) -> dict:
    if len(body) > 262144:
        raise ValueError("delivery exceeds the rehearsal limit")
    if not secret:
        raise ValueError("missing webhook secret")
    h = {key.lower(): value for key, value in headers.items()}
    supplied = h.get("x-shopify-hmac-sha256", "")
    expected = base64.b64encode(hmac.digest(secret, body, hashlib.sha256)).decode("ascii")
    if (
        not isinstance(supplied, str)
        or not supplied.isascii()
        or not hmac.compare_digest(supplied, expected)
    ):
        raise ValueError("invalid delivery signature")
    if h.get("x-shopify-shop-domain") != expected_shop or h.get("x-shopify-topic") != "orders/paid":
        raise ValueError("unexpected shop or topic")
    # Authenticating the delivery does not admit non-test orders to the rehearsal.
    data = json.loads(body)
    if not isinstance(data, dict) or data.get("test") is not True:
        raise ValueError("rehearsal requires a test order")
    address = data["shipping_address"]
    keep = ("first_name", "last_name", "address1", "city", "zip", "country_code", "province_code")
    return {
        "shop": expected_shop,
        "id": data["id"],
        "test": True,
        "financial_status": data["financial_status"],
        "currency": data["currency"],
        "line_items": [
            {k: item[k] for k in ("sku", "quantity", "price")} for item in data["line_items"]
        ],
        "shipping_address": {k: address[k] for k in keep if k in address},
    }


def redacted_draft(draft: dict) -> dict:
    """The supplier transport needs an address; evidence and MCP outputs need only the route."""
    payload = draft["body"]
    return {
        "mode": "dry_run",
        "method": draft["method"],
        "path": draft["path"],
        "external_id": payload["external_id"],
        "items": payload["items"],
        "destination_country": payload["recipient"]["country_code"],
    }
