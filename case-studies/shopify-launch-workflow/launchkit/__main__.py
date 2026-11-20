import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
from pydantic import ValidationError

from .artifacts import build, write_json
from .creative import CreativeChoice, render_copy
from .orders import Ledger
from .privacy import normalize_delivery, redacted_draft
from .providers import audit_draft, read_printful, read_shopify, select_rate
from .spec import Brief, evaluate
from .staging import stage_dev

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def generate(brief, target, choice, fixtures=None):
    if target.exists():
        raise ValueError("choose a new output directory for each run")
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=target.parent) as temp:
        work = Path(temp) / "bundle"
        outcome = evaluate(brief)
        copy = render_copy(brief, choice) if outcome["decision"] == "READY_FOR_REHEARSAL" else None
        build(brief, work, copy, outcome)
        if fixtures is not None and copy is not None:
            rate = select_rate(brief, read_json(fixtures / "printful-rates.json"))
            if (
                rate["per_unit"] != f"{brief.shipping.per_unit:.2f}"
                or rate["max_days"] > brief.shipping.max_days
            ):
                raise ValueError(
                    "supplier quote differs from the merchant brief; re-price the offer"
                )
            audit = audit_draft(brief, read_json(fixtures / "shopify-readback.json"))
            if not audit["matches"]:
                raise ValueError("catalog audit failed: " + ", ".join(audit["issues"]))
            orders = Ledger(work / "rehearsal.sqlite")
            order = normalize_delivery(
                (fixtures / "shopify-paid-webhook.json").read_bytes(),
                read_json(fixtures / "delivery-headers.json"),
                brief.shop,
                b"public-rehearsal-key",
            )
            draft = orders.stage(brief, order)
            draft["dry_run_supplier_request"] = redacted_draft(draft["dry_run_supplier_request"])
            replay = orders.stage(brief, order)
            shipment = orders.shipment(brief.shop, read_json(fixtures / "shipment.json"))
            write_json(
                work / "rehearsal.json",
                {
                    "mode": "offline_fixtures",
                    "rate": rate,
                    "catalog": audit,
                    "first_delivery": draft,
                    "duplicate_delivery": replay,
                    "shipment": shipment,
                },
            )
        work.rename(target)
    return outcome


def cli():
    parser = argparse.ArgumentParser(
        description="Plan and rehearse one SKU, one market and one supplier."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "rehearse", "shopify-readback", "printful-rate", "stage-dev-draft"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--brief", type=Path, default=EXAMPLES / "brief.json")
        if name in ("build", "rehearse"):
            cmd.add_argument("--out", type=Path, required=True)
            cmd.add_argument("--copy", type=Path, default=EXAMPLES / "creative-choice.json")
        if name == "rehearse":
            cmd.add_argument("--fixtures", type=Path, default=EXAMPLES)
        if name == "stage-dev-draft":
            cmd.add_argument("--confirm-shop", required=True)
            cmd.add_argument("--copy", type=Path, default=EXAMPLES / "creative-choice.json")
        if name == "printful-rate":
            cmd.add_argument("--city", required=True)
            cmd.add_argument("--postal", required=True)
            cmd.add_argument("--state")
    args = parser.parse_args()
    try:
        brief = Brief.model_validate(read_json(args.brief))
        if args.command in ("build", "rehearse"):
            choice = CreativeChoice.model_validate(read_json(args.copy))
            result = generate(brief, args.out, choice, getattr(args, "fixtures", None))
        else:
            with httpx.Client(timeout=15, trust_env=False) as http:
                if args.command == "stage-dev-draft":
                    choice = CreativeChoice.model_validate(read_json(args.copy))
                    result = stage_dev(
                        brief, choice, args.confirm_shop, os.environ["SHOPIFY_ADMIN_TOKEN"], http
                    )
                elif args.command == "shopify-readback":
                    result = read_shopify(brief, os.environ["SHOPIFY_ADMIN_TOKEN"], http)
                else:
                    result = read_printful(
                        brief,
                        os.environ["PRINTFUL_TOKEN"],
                        args.postal,
                        args.city,
                        args.state,
                        http,
                    )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get("decision") == "HOLD" or result.get("matches") is False else 0
    except ValidationError as exc:
        for error in exc.errors(include_input=False, include_url=False):
            print(f"{'.'.join(map(str, error['loc']))}: {error['msg']}", file=sys.stderr)
    except (ValueError, OSError, KeyError, httpx.HTTPError) as exc:
        print(str(exc), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(cli())
