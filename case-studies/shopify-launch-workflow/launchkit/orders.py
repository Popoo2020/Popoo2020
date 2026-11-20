"""Rehearse one paid test unit per order. SQLite makes replay and conflicting events observable."""

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictBool

from .spec import Amount, Brief, evaluate


class TestAddress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    address1: str = Field(min_length=1)
    city: str = Field(min_length=1)
    zip: str = Field(min_length=1)
    country_code: str
    province_code: str | None = None


class LineItem(BaseModel):
    sku: str
    quantity: Annotated[int, Field(strict=True, gt=0)]
    price: Amount


class PaidOrder(BaseModel):
    shop: str
    id: Annotated[int, Field(strict=True, gt=0)]
    test: StrictBool
    financial_status: str
    currency: str
    line_items: list[LineItem]
    shipping_address: TestAddress


def prepare_supplier_draft(brief: Brief, raw: dict) -> tuple[PaidOrder, dict]:
    if evaluate(brief)["decision"] != "READY_FOR_REHEARSAL":
        raise ValueError("launch is on HOLD")
    order = PaidOrder.model_validate(raw)
    if not order.test or order.shop != brief.shop or order.financial_status != "paid":
        raise ValueError("only paid test orders for the configured shop are accepted")
    if order.currency != brief.currency or order.shipping_address.country_code != brief.market:
        raise ValueError("unexpected currency or shipping destination")
    if len(order.line_items) != 1:
        raise ValueError("the rehearsal accepts exactly one quoted unit")
    item = order.line_items[0]
    if (
        item.quantity != 1
        or item.sku != brief.product.sku
        or item.price != brief.product.sale_price
    ):
        raise ValueError("line item does not match the single-unit offer")
    address = order.shipping_address
    recipient = {
        "name": f"{address.first_name} {address.last_name}",
        "address1": address.address1,
        "city": address.city,
        "zip": address.zip,
        "country_code": address.country_code,
    }
    if address.province_code:
        recipient["state_code"] = address.province_code
    payload = {
        "external_id": f"demo-{order.id}",
        "recipient": recipient,
        "items": [{"sync_variant_id": brief.supplier.sync_variant_id, "quantity": 1}],
    }
    return order, payload


class Ledger:
    def __init__(self, path: Path):
        self.path = path
        with closing(self._open()) as db, db:
            db.execute("""CREATE TABLE IF NOT EXISTS orders (
                shop TEXT NOT NULL, order_id INTEGER NOT NULL, digest TEXT NOT NULL,
                state TEXT NOT NULL, tracking TEXT, carrier TEXT,
                PRIMARY KEY(shop, order_id))""")

    def _open(self):
        return sqlite3.connect(self.path, timeout=10)

    def stage(self, brief: Brief, raw: dict) -> dict:
        order, payload = prepare_supplier_draft(brief, raw)
        item = order.line_items[0]
        digest_input = [payload, item.sku, f"{item.price:.2f}", order.currency]
        digest = hashlib.sha256(json.dumps(digest_input, sort_keys=True).encode()).hexdigest()
        with closing(self._open()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT digest, state FROM orders WHERE shop=? AND order_id=?",
                (brief.shop, order.id),
            ).fetchone()
            if existing:
                if existing[0] != digest:
                    raise ValueError("conflicting replay for an existing order")
                return {"state": existing[1], "replay": True, "order_id": order.id}
            db.execute(
                "INSERT INTO orders VALUES (?, ?, ?, 'DRAFT_PREPARED', NULL, NULL)",
                (brief.shop, order.id, digest),
            )
        return {
            "state": "DRAFT_PREPARED",
            "replay": False,
            "order_id": order.id,
            "dry_run_supplier_request": {
                "method": "POST",
                "path": "/orders?confirm=false",
                "body": payload,
            },
        }

    def shipment(self, shop: str, event: dict) -> dict:
        if event.get("type") != "package_shipped":
            raise ValueError("expected a package_shipped fixture")
        try:
            data = event["data"]
            external = data["order"]["external_id"]
            prefix, suffix = external.split("-", 1)
            if prefix != "demo" or not suffix.isascii() or not suffix.isdecimal():
                raise ValueError("invalid test order reference")
            order_id = int(suffix)
            tracking = data["shipment"]["tracking_number"]
            carrier = data["shipment"]["carrier"]
            if not all(isinstance(v, str) and v.strip() for v in (tracking, carrier)):
                raise ValueError("missing shipment details")
        except (AttributeError, KeyError, TypeError) as exc:
            raise ValueError("incomplete shipment fixture") from exc
        with closing(self._open()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT state, tracking, carrier FROM orders WHERE shop=? AND order_id=?",
                (shop, order_id),
            ).fetchone()
            if row is None:
                raise ValueError("unknown order; reconcile before recording shipment")
            if row[0] == "TRACKING_REHEARSED":
                if (tracking, carrier) != row[1:]:
                    raise ValueError("conflicting shipment replay")
                return {"state": row[0], "replay": True, "order_id": order_id}
            db.execute(
                "UPDATE orders SET state='TRACKING_REHEARSED', tracking=?, carrier=? WHERE shop=? AND order_id=?",
                (tracking, carrier, shop, order_id),
            )
        return {
            "state": "TRACKING_REHEARSED",
            "replay": False,
            "order_id": order_id,
            "merchant_handoff": {"carrier": carrier, "tracking_number": tracking},
        }
