from .spec import Brief


def merchant_report(brief: Brief, outcome: dict) -> str:
    lines = [
        f"# Launch decision for {brief.product.sku}",
        "",
        f"**{outcome['decision']}** on {brief.as_of}. All figures use {brief.currency}.",
        "",
        f"Company and market: {outcome['company_to_market']}. Supplier and customer: {outcome['supplier_to_customer']}.",
        "",
        "## Commercial decision",
        "",
    ]
    economics = outcome["economics"]
    if economics:
        lines += [
            "| Per-order or cash measure | Amount |",
            "|---|---:|",
            f"| Selling price | {brief.product.sale_price:.2f} |",
            f"| Product and outbound delivery | {economics['supplier_outlay_per_order']} |",
            f"| Payment fee | {economics['payment_fee']} |",
            f"| Break-even acquisition cost | {economics['break_even_cac']} |",
            f"| Planned acquisition cost | {brief.marketing.target_cac:.2f} |",
            f"| Contribution after planned acquisition | {economics['contribution_after_target_cac']} |",
            f"| Launch cash required | {economics['cash_committed']} |",
            f"| Cash remaining or shortfall | {economics['cash_remaining']} |",
            "",
            "Contribution deducts the merchant's tax, duty and return allowances. Acquisition cost is an assumption. Fixed overhead and actual conversion are outside this estimate.",
        ]
    else:
        lines += [
            "Requote the actual SKU, origin, destination and currency before evaluating contribution."
        ]
    if outcome["blocks"]:
        actions = {
            "new_shipping_quote_needed": "Request a quote for this variant, origin, destination and currency.",
            "shipping_quote_expired": "Refresh the expired supplier quote.",
            "delivery_promise_unsupported": "Change the delivery promise or choose a faster service.",
            "supplier_sample_needed": "Check a physical sample and the supplier's fulfilment terms.",
            "company_and_market_review_needed": "Review the legal entity, fulfilment origin and target market together.",
            "review_payment_eligibility": "Verify payout eligibility for the merchant's legal entity.",
            "review_tax_and_returns": "Confirm applicable taxes, import terms and the return route.",
            "acquisition_spend_erases_contribution": "Re-price the offer, reduce landed cost or validate a lower acquisition cost.",
            "insufficient_launch_cash": "Reduce the committed spend or provide sufficient working capital.",
            "marketing_test_underfunded": "Review the campaign budget against the proposed acquisition cost.",
        }
        lines += [
            "",
            "## Resolve before staging",
            "",
            *["- " + actions[b] for b in outcome["blocks"]],
        ]
    else:
        lines += [
            "",
            "## Owner decision",
            "",
            outcome["handover"],
            "Approve product facts, shipping promise, campaign cap and a test order before publishing or spending.",
        ]
    return "\n".join(lines) + "\n"
