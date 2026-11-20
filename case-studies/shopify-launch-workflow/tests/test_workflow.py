import csv
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

import httpx
from launchkit.__main__ import EXAMPLES, generate, read_json
from launchkit.creative import CreativeChoice, render_copy
from launchkit.orders import Ledger
from launchkit.providers import audit_draft, read_printful, read_shopify, select_rate
from launchkit.spec import Brief, evaluate
from pydantic import ValidationError


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.raw = read_json(EXAMPLES / "brief.json")
        self.brief = Brief.model_validate(self.raw)
        self.choice = CreativeChoice.model_validate(read_json(EXAMPLES / "creative-choice.json"))
        self.order = dict(read_json(EXAMPLES / "shopify-paid-webhook.json"), shop=self.brief.shop)
        self.shipment = read_json(EXAMPLES / "shipment.json")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    def changed(self, section, **values):
        data = deepcopy(self.raw)
        data[section].update(values)
        return Brief.model_validate(data)

    def test_costs_include_fees_returns_and_cash_float(self):
        result = evaluate(self.brief)
        self.assertEqual(result["decision"], "READY_FOR_REHEARSAL")
        self.assertEqual(
            result["economics"],
            {
                "payment_fee": "1.28",
                "supplier_outlay_per_order": "16.50",
                "break_even_cac": "13.52",
                "contribution_after_target_cac": "5.52",
                "cash_committed": "670.00",
                "cash_remaining": "330.00",
            },
        )
        result = evaluate(self.changed("product", duty_allowance="2.00"))
        self.assertEqual(result["economics"]["contribution_after_target_cac"], "3.52")

    def test_held_brief_generates_only_decision(self):
        brief = Brief.model_validate(read_json(EXAMPLES / "hold-brief.json"))
        out = self.work / "held"
        result = generate(brief, out, self.choice, EXAMPLES)
        self.assertEqual(
            set(result["blocks"]),
            {"acquisition_spend_erases_contribution", "insufficient_launch_cash"},
        )
        self.assertEqual({p.name for p in out.iterdir()}, {"decision.json", "merchant-report.md"})

    def test_stale_mismatched_or_wrong_variant_never_computes_landed_cost(self):
        for change in (
            {"market": "US"},
            {"currency": "USD"},
            {"valid_until": "2026-01-01"},
            {"dispatch_country": "US"},
            {"catalog_variant_id": 2},
        ):
            with self.subTest(change=change):
                result = evaluate(self.changed("shipping", **change))
                self.assertEqual(result["decision"], "HOLD")
                self.assertIsNone(result["economics"])

    def test_company_country_and_experience_change_the_handoff(self):
        raw = dict(self.raw, company_country="GB", experience="experienced")
        result = evaluate(Brief.model_validate(raw))
        self.assertIn("company_and_market_review_needed", result["blocks"])
        self.assertNotEqual(result["handover"], evaluate(self.brief)["handover"])

    def test_economic_and_operational_stop_conditions(self):
        for section, fields, block in (
            ("market_review", {"payouts_checked": False}, "review_payment_eligibility"),
            ("market_review", {"tax_and_returns_checked": False}, "review_tax_and_returns"),
            ("supplier", {"sample_checked": False}, "supplier_sample_needed"),
            ("shipping", {"max_days": 9}, "delivery_promise_unsupported"),
            ("budget", {"marketing_test": "2.00"}, "marketing_test_underfunded"),
            ("marketing", {"target_cac": "13.52"}, "acquisition_spend_erases_contribution"),
        ):
            with self.subTest(block=block):
                self.assertIn(block, evaluate(self.changed(section, **fields))["blocks"])

    def test_bad_domain_and_money_are_rejected(self):
        for data in (
            dict(self.raw, shop="sample.myshopify.com.evil.example"),
            dict(self.raw, shop="user@sample.myshopify.com"),
            dict(self.raw, currency="ZZZ"),
            dict(self.raw, product=dict(self.raw["product"], sale_price="NaN")),
            dict(self.raw, product=dict(self.raw["product"], title="=SUM(1)")),
            dict(self.raw, product=dict(self.raw["product"], unit_cost="-1.00")),
        ):
            with self.assertRaises(ValidationError):
                Brief.model_validate(data)

    def test_marketing_output_uses_only_approved_facts(self):
        copy = render_copy(self.brief, self.choice)
        self.assertEqual(copy["headline"], "Blue grid illustration")
        bad = self.choice.model_copy(update={"lead_fact": 12})
        with self.assertRaises(ValueError):
            render_copy(self.brief, bad)
        with self.assertRaises(ValueError):
            render_copy(self.brief, self.choice.model_copy(update={"supporting_facts": [2]}))

    def test_catalog_and_campaign_are_merchant_reviewable(self):
        out = self.work / "ready"
        generate(self.brief, out, self.choice, EXAMPLES)
        with (out / "shopify-draft.csv").open(newline="") as stream:
            (row,) = csv.DictReader(stream)
        self.assertEqual(
            (row["Status"], row["Published on online store"], row["SKU"]),
            ("draft", "false", "DEMO-PRINT-A4"),
        )
        self.assertNotIn("qualified visits", row["Description"])
        campaign = read_json(out / "campaign.json")
        self.assertIn("utm_campaign=grid-launch-de", campaign["landing_path"])
        self.assertEqual(campaign["creative_draft"]["cta"], "See print details")
        trace = read_json(out / "rehearsal.json")
        self.assertTrue(trace["duplicate_delivery"]["replay"])
        self.assertEqual(trace["shipment"]["state"], "TRACKING_REHEARSED")
        with self.assertRaises(ValueError):
            generate(self.brief, out, self.choice)

    def test_failed_run_is_safe_to_retry(self):
        out = self.work / "bundle"
        with self.assertRaisesRegex(ValueError, "re-price"):
            generate(self.changed("shipping", per_unit="3.00"), out, self.choice, EXAMPLES)
        self.assertFalse(out.exists())
        generate(self.brief, out, self.choice, EXAMPLES)
        self.assertTrue((out / "rehearsal.json").exists())

    def test_persistent_replay_and_conflict(self):
        path = self.work / "state.sqlite"
        ledger = Ledger(path)
        first = ledger.stage(self.brief, self.order)
        self.assertEqual(
            first["dry_run_supplier_request"]["body"]["items"],
            [{"sync_variant_id": 90001, "quantity": 1}],
        )
        self.assertTrue(Ledger(path).stage(self.brief, self.order)["replay"])
        self.order["shipping_address"]["city"] = "Other city"
        with self.assertRaisesRegex(ValueError, "conflicting"):
            ledger.stage(self.brief, self.order)
        with sqlite3.connect(path) as db:
            content = str(db.execute("SELECT * FROM orders").fetchall())
        self.assertNotIn("Example address", content)

    def test_concurrent_duplicate_order_is_staged_once(self):
        ledger = Ledger(self.work / "state.sqlite")
        with ThreadPoolExecutor(max_workers=4) as workers:
            results = list(workers.map(lambda _: ledger.stage(self.brief, self.order), range(4)))
        self.assertEqual(sum(not result["replay"] for result in results), 1)

    def test_live_unpaid_wrong_shop_and_unquoted_basket_are_declined(self):
        ledger = Ledger(self.work / "state.sqlite")
        for order in (
            dict(self.order, test=False),
            dict(self.order, financial_status="pending"),
            dict(self.order, shop="another.myshopify.com"),
            dict(self.order, currency="USD"),
            dict(
                self.order, line_items=[{"sku": "DEMO-PRINT-A4", "quantity": 2, "price": "39.00"}]
            ),
            dict(
                self.order, shipping_address=dict(self.order["shipping_address"], country_code="US")
            ),
        ):
            with self.assertRaises(ValueError):
                ledger.stage(self.brief, order)

    def test_tracking_replay_and_conflict(self):
        ledger = Ledger(self.work / "state.sqlite")
        with self.assertRaisesRegex(ValueError, "unknown order"):
            ledger.shipment(self.brief.shop, self.shipment)
        ledger.stage(self.brief, self.order)
        self.assertFalse(ledger.shipment(self.brief.shop, self.shipment)["replay"])
        self.assertTrue(ledger.shipment(self.brief.shop, self.shipment)["replay"])
        self.shipment["data"]["shipment"]["tracking_number"] = "DIFFERENT"
        with self.assertRaisesRegex(ValueError, "conflicting"):
            ledger.shipment(self.brief.shop, self.shipment)

    def test_shopify_contract_and_errors(self):
        raw = read_json(EXAMPLES / "shopify-readback.json")

        def handler(request):
            self.assertEqual(
                str(request.url), f"https://{self.brief.shop}/admin/api/2026-07/graphql.json"
            )
            self.assertEqual(request.headers["X-Shopify-Access-Token"], "fixture")
            self.assertEqual(
                json.loads(request.content)["variables"], {"search": "handle:grid-studio-print"}
            )
            return httpx.Response(200, json=raw, headers={"X-Shopify-API-Version": "2026-07"})

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            self.assertTrue(read_shopify(self.brief, "fixture", client)["matches"])
        raw["data"]["products"]["nodes"][0]["status"] = "ACTIVE"
        self.assertIn("product_status", audit_draft(self.brief, raw)["issues"])
        with self.assertRaises(ValueError):
            audit_draft(self.brief, {"errors": [{"message": "access denied"}]})

    def test_printful_rate_contract_filters_options(self):
        raw = read_json(EXAMPLES / "printful-rates.json")
        raw["result"] += [
            dict(raw["result"][0], rate="0.01", maxDeliveryDays=20),
            dict(raw["result"][0], currency="USD"),
        ]

        def handler(request):
            self.assertEqual(
                (request.method, str(request.url)),
                ("POST", "https://api.printful.com/shipping/rates"),
            )
            body = json.loads(request.content)
            self.assertEqual(body["items"], [{"variant_id": 10001, "quantity": 1}])
            self.assertEqual(body["recipient"]["country_code"], "DE")
            return httpx.Response(200, json=raw)

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            self.assertEqual(
                read_printful(self.brief, "fixture", "10115", "Berlin", None, client)["per_unit"],
                "4.50",
            )
        with self.assertRaises(ValueError):
            select_rate(self.brief, {"code": 200, "result": []})


if __name__ == "__main__":
    unittest.main()
