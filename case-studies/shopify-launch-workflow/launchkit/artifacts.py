"""Materialize a draft catalog and a bounded marketing experiment from approved facts."""

import csv
import json
from pathlib import Path
from urllib.parse import urlencode

from .creative import product_description
from .report import merchant_report
from .spec import Brief
from .staging import draft_request


def campaign(brief: Brief, copy: dict) -> dict:
    p, m = brief.product, brief.marketing
    source, medium = {
        "paid_search": ("google", "cpc"),
        "paid_social": ("meta", "paid_social"),
        "partner_email": ("partner", "email"),
    }[m.channel]
    query = urlencode({"utm_source": source, "utm_medium": medium, "utm_campaign": m.campaign})
    return {
        "channel": m.channel,
        "approved_facts": p.facts,
        "creative_draft": copy,
        "campaign_cap": str(brief.budget.marketing_test),
        "target_cac": str(m.target_cac),
        "currency": brief.currency,
        "landing_path": f"/products/{p.handle}?{query}",
        "measurement": "Track spend, attributed paid orders and refunds. CAC = spend / new paying customers. Report no observed CAC when there are zero.",
        "stop_rule": "Pause at the test cap, or when the agreed threshold is exceeded after the owner's review. Obtain owner approval for wording, targeting and spend.",
    }


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(brief: Brief, out: Path, copy: dict | None, report: dict) -> None:
    # Every run writes into a new directory so a HOLD can never inherit an older CSV.
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "decision.json", report)
    (out / "merchant-report.md").write_text(merchant_report(brief, report), encoding="utf-8")
    if report["decision"] == "HOLD":
        return
    p = brief.product
    description = product_description(copy)
    row = {
        "Title": p.title,
        "URL handle": p.handle,
        "Description": description,
        "Status": "draft",
        "Published on online store": "false",
        "Option1 name": "Title",
        "Option1 value": "Default Title",
        "SKU": p.sku,
        "Price": f"{p.sale_price:.2f}",
        "Requires shipping": "true",
    }
    with (out / "shopify-draft.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        writer.writeheader()
        writer.writerow(row)
    write_json(out / "shopify-admin-draft.json", draft_request(brief, copy))
    write_json(out / "campaign.json", campaign(brief, copy))
