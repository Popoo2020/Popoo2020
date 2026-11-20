import json
import unittest
from copy import deepcopy
from datetime import date

import httpx
from launchkit.__main__ import EXAMPLES, read_json
from launchkit.creative import CreativeChoice
from launchkit.spec import Brief
from launchkit.staging import stage_dev


class DevelopmentStagingTests(unittest.TestCase):
    def setUp(self):
        self.brief = Brief.model_validate(read_json(EXAMPLES / "brief.json"))
        self.choice = CreativeChoice.model_validate(read_json(EXAMPLES / "creative-choice.json"))
        self.before = read_json(EXAMPLES / "shopify-readback.json")
        self.product = self.before["data"]["products"]["nodes"].pop()
        self.requests = []

    def exchange(self, responses, confirm=None):
        def handler(request):
            payload = json.loads(request.content)
            self.requests.append(payload)
            return httpx.Response(200, json=responses.pop(0))

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            return stage_dev(
                self.brief,
                self.choice,
                confirm or self.brief.shop,
                "fixture-token",
                client,
                today=date(2026, 11, 20),
            )

    def test_create_only_draft_contract(self):
        result = self.exchange(
            [self.before, {"data": {"productSet": {"product": self.product, "userErrors": []}}}]
        )
        self.assertEqual(result["state"], "DEVELOPMENT_DRAFT_CREATED")
        variables = self.requests[1]["variables"]
        self.assertEqual(set(variables), {"input"})
        value = variables["input"]
        self.assertEqual(value["status"], "DRAFT")
        self.assertNotIn("id", value)
        self.assertEqual(value["variants"][0]["inventoryItem"]["sku"], self.brief.product.sku)
        self.assertEqual(value["variants"][0]["price"], "39.00")

    def test_real_store_wrong_currency_and_existing_product_never_write(self):
        for patch in (
            {"plan": {"partnerDevelopment": False}},
            {"currencyCode": "USD"},
            {"myshopifyDomain": "other.myshopify.com"},
        ):
            with self.subTest(patch=patch):
                before = deepcopy(self.before)
                before["data"]["shop"].update(patch)
                self.requests.clear()
                with self.assertRaises(ValueError):
                    self.exchange([before])
                self.assertEqual(len(self.requests), 1)
        self.requests.clear()
        self.before["data"]["products"]["nodes"].append(self.product)
        with self.assertRaisesRegex(ValueError, "untouched"):
            self.exchange([self.before])
        self.assertEqual(len(self.requests), 1)

    def test_confirmation_and_hold_run_before_network(self):
        with self.assertRaises(ValueError):
            self.exchange([], confirm="wrong.myshopify.com")
        self.brief = Brief.model_validate(read_json(EXAMPLES / "hold-brief.json"))
        with self.assertRaises(ValueError):
            self.exchange([])
        self.assertEqual(self.requests, [])

    def test_mutation_rejection_is_not_retried(self):
        with self.assertRaisesRegex(ValueError, "declined"):
            self.exchange(
                [
                    self.before,
                    {
                        "data": {
                            "productSet": {
                                "product": None,
                                "userErrors": [{"message": "handle in use"}],
                            }
                        }
                    },
                ]
            )
        self.assertEqual(len(self.requests), 2)
