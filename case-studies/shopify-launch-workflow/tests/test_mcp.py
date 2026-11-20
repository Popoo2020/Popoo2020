import json
import sys
import unittest

from launchkit.__main__ import EXAMPLES, read_json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_client_can_plan_price_and_prepare_an_order(self):
        params = StdioServerParameters(command=sys.executable, args=["-m", "launchkit.mcp_server"])
        async with (
            stdio_client(params) as (reader, writer),
            ClientSession(reader, writer) as session,
        ):
            await session.initialize()
            tools = await session.list_tools()
            self.assertEqual(
                {t.name for t in tools.tools},
                {
                    "evaluate_store",
                    "preview_merchandising",
                    "assess_supplier_rates",
                    "preview_supplier_order",
                },
            )
            brief = read_json(EXAMPLES / "brief.json")
            result = await session.call_tool("evaluate_store", {"brief": brief})
            self.assertFalse(result.isError)
            self.assertIn("13.52", result.content[0].text)
            prompt = await session.get_prompt(
                "plan_catalog_copy",
                {"title": "Print", "facts_json": json.dumps(brief["product"]["facts"])},
            )
            self.assertIn("zero-based", prompt.messages[0].content.text)
            choices = read_json(EXAMPLES / "creative-choice.json")
            creative = await session.call_tool(
                "preview_merchandising", {"facts": brief["product"]["facts"], "choice": choices}
            )
            self.assertFalse(creative.isError)
            rates = await session.call_tool(
                "assess_supplier_rates",
                {"brief": brief, "response": read_json(EXAMPLES / "printful-rates.json")},
            )
            self.assertIn("4.50", rates.content[0].text)
            order = {"id": 1001, "sku": "DEMO-PRINT-A4", "quantity": 1, "test": True}
            draft = await session.call_tool(
                "preview_supplier_order", {"brief": brief, "test_order": order}
            )
            self.assertFalse(draft.isError)
            self.assertIn("confirm=false", draft.content[0].text)
            order["test"] = False
            invalid = await session.call_tool(
                "preview_supplier_order", {"brief": brief, "test_order": order}
            )
            self.assertTrue(invalid.isError)
