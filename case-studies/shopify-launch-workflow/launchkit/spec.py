"""Typed, single-SKU launch brief. All monetary inputs use the same shop currency."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

Country = Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
Currency = Literal["EUR", "USD", "GBP", "DKK", "AUD", "SEK", "SGD"]
Amount = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
PositiveAmount = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
PositiveCount = Annotated[int, Field(strict=True, ge=1, le=100000)]
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", max_length=128)]
Shop = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*\.myshopify\.com$", max_length=145)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Budget(StrictModel):
    cash: PositiveAmount
    setup: Amount
    samples: Amount
    marketing_test: Amount
    float_units: PositiveCount


class Product(StrictModel):
    handle: Slug
    title: Annotated[str, Field(min_length=1, max_length=120)]
    sku: Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")]
    facts: Annotated[list[str], Field(min_length=1, max_length=8)]
    sale_price: PositiveAmount
    unit_cost: PositiveAmount
    payment_percent: Annotated[Decimal, Field(ge=0, le=100, decimal_places=3)]
    payment_fixed: Amount
    tax_allowance: Amount
    return_allowance: Amount
    duty_allowance: Amount

    @field_validator("title")
    @classmethod
    def printable_title(cls, value):
        if value[0] in "=+-@" or not value.isprintable():
            raise ValueError("use plain printable text for the CSV title")
        return value

    @field_validator("facts")
    @classmethod
    def printable_facts(cls, values):
        if any(not fact.strip() or not fact.isprintable() or len(fact) > 180 for fact in values):
            raise ValueError("facts must contain 1–180 printable characters")
        return values


class Supplier(StrictModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    dispatch_country: Country
    catalog_variant_id: Annotated[int, Field(strict=True, gt=0)]
    sync_variant_id: Annotated[int, Field(strict=True, gt=0)]
    sample_checked: StrictBool


class Quote(StrictModel):
    market: Country
    dispatch_country: Country
    catalog_variant_id: Annotated[int, Field(strict=True, gt=0)]
    currency: Currency
    per_unit: Amount
    max_days: PositiveCount
    valid_until: date


class MarketReview(StrictModel):
    company_country: Country
    dispatch_country: Country
    market: Country
    payouts_checked: StrictBool
    tax_and_returns_checked: StrictBool


class Marketing(StrictModel):
    channel: Literal["paid_search", "paid_social", "partner_email"]
    target_cac: PositiveAmount
    max_delivery_days: PositiveCount
    campaign: Slug


class Brief(StrictModel):
    as_of: date
    shop: Shop
    company_country: Country
    market: Country
    currency: Currency
    experience: Literal["first_store", "experienced"]
    budget: Budget
    product: Product
    supplier: Supplier
    shipping: Quote
    market_review: MarketReview
    marketing: Marketing


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def evaluate(brief: Brief) -> dict:
    product, shipping, budget = brief.product, brief.shipping, brief.budget
    blocks = []
    if (
        shipping.market,
        shipping.currency,
        shipping.dispatch_country,
        shipping.catalog_variant_id,
    ) != (
        brief.market,
        brief.currency,
        brief.supplier.dispatch_country,
        brief.supplier.catalog_variant_id,
    ):
        blocks.append("new_shipping_quote_needed")
    if shipping.valid_until < brief.as_of:
        blocks.append("shipping_quote_expired")
    if shipping.max_days > brief.marketing.max_delivery_days:
        blocks.append("delivery_promise_unsupported")
    if not brief.supplier.sample_checked:
        blocks.append("supplier_sample_needed")
    review = brief.market_review
    if (review.company_country, review.market, review.dispatch_country) != (
        brief.company_country,
        brief.market,
        brief.supplier.dispatch_country,
    ):
        blocks.append("company_and_market_review_needed")
    if not review.payouts_checked:
        blocks.append("review_payment_eligibility")
    if not review.tax_and_returns_checked:
        blocks.append("review_tax_and_returns")

    fee = money(product.sale_price * product.payment_percent / 100 + product.payment_fixed)
    economics = None
    if "new_shipping_quote_needed" not in blocks and "shipping_quote_expired" not in blocks:
        unit_outlay = product.unit_cost + shipping.per_unit
        max_cac = money(
            product.sale_price
            - unit_outlay
            - fee
            - product.tax_allowance
            - product.duty_allowance
            - product.return_allowance
        )
        contribution = money(max_cac - brief.marketing.target_cac)
        committed = money(
            budget.setup + budget.samples + budget.marketing_test + budget.float_units * unit_outlay
        )
        headroom = money(budget.cash - committed)
        if contribution <= 0:
            blocks.append("acquisition_spend_erases_contribution")
        if headroom < 0:
            blocks.append("insufficient_launch_cash")
        if budget.marketing_test < brief.marketing.target_cac:
            blocks.append("marketing_test_underfunded")
        economics = {
            k: str(money(v))
            for k, v in {
                "payment_fee": fee,
                "supplier_outlay_per_order": unit_outlay,
                "break_even_cac": max_cac,
                "contribution_after_target_cac": contribution,
                "cash_committed": committed,
                "cash_remaining": headroom,
            }.items()
        }
    next_step = (
        "Walk through a sample order with the owner before running the campaign."
        if brief.experience == "first_store"
        else "Have the operator sign off on exceptions and the first campaign cohort."
    )
    return {
        "decision": "HOLD" if blocks else "READY_FOR_REHEARSAL",
        "blocks": blocks,
        "currency": brief.currency,
        "economics": economics,
        "company_to_market": f"{brief.company_country} → {brief.market}",
        "supplier_to_customer": f"{brief.supplier.dispatch_country} → {brief.market}",
        "handover": next_step,
    }
