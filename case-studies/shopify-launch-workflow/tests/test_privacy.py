import base64
import hmac
import json
import tempfile
import unittest
from pathlib import Path

from launchkit.__main__ import EXAMPLES, generate, read_json
from launchkit.creative import CreativeChoice
from launchkit.mcp_server import OrderPreview, preview_supplier_order
from launchkit.privacy import normalize_delivery
from launchkit.spec import Brief
from pydantic import ValidationError


class PrivacyControls(unittest.TestCase):
    def setUp(self):
        self.brief = Brief.model_validate(read_json(EXAMPLES / "brief.json"))
        self.body = (EXAMPLES / "shopify-paid-webhook.json").read_bytes()
        self.headers = read_json(EXAMPLES / "delivery-headers.json")
        self.key = b"public-rehearsal-key"

    def normalize(self, body=None, headers=None):
        return normalize_delivery(
            self.body if body is None else body,
            self.headers if headers is None else headers,
            self.brief.shop,
            self.key,
        )

    def test_tamper_wrong_topic_and_unknown_shop(self):
        self.assertEqual(self.normalize()["id"], 1001)
        with self.assertRaisesRegex(ValueError, "signature"):
            self.normalize(self.body + b" ")
        for name in ("X-Shopify-Topic", "X-Shopify-Shop-Domain", "X-Shopify-Hmac-Sha256"):
            with self.assertRaises(ValueError):
                self.normalize(headers=dict(self.headers, **{name: "wrong"}))

    def test_normalizer_drops_contact_fields_before_workflow(self):
        data = json.loads(self.body)
        data["email"] = "private@example.invalid"
        data["shipping_address"]["phone"] = "sample-private-phone"
        body = json.dumps(data).encode()
        heads = dict(
            self.headers,
            **{
                "X-Shopify-Hmac-Sha256": base64.b64encode(
                    hmac.digest(self.key, body, "sha256")
                ).decode()
            },
        )
        text = json.dumps(self.normalize(body, heads))
        self.assertNotIn("example.invalid", text)
        self.assertNotIn("sample-private-phone", text)

    def test_mcp_order_schema_rejects_address_and_outputs_country_only(self):
        inp = {"id": 1001, "sku": "DEMO-PRINT-A4", "quantity": 1, "test": True}
        with self.assertRaises(ValidationError):
            OrderPreview.model_validate(dict(inp, shipping_address={"address1": "DO-NOT-SHARE"}))
        preview = preview_supplier_order(self.brief, OrderPreview.model_validate(inp))
        self.assertEqual(preview["destination_country"], "DE")
        self.assertNotIn("recipient", json.dumps(preview))
        self.assertNotIn("zip", json.dumps(preview))

    def test_saved_artifacts_exclude_delivery_address(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle"
            generate(
                self.brief,
                out,
                CreativeChoice.model_validate(read_json(EXAMPLES / "creative-choice.json")),
                EXAMPLES,
            )
            for path in out.iterdir():
                data = path.read_bytes()
                for private_value in (
                    b"Example address 1",
                    b"Demo Recipient",
                    b"10115",
                    b"public-rehearsal-key",
                ):
                    self.assertNotIn(private_value, data, path.name)
