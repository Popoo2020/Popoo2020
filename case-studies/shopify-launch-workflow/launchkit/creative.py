"""Render an AI client's merchandising choices from merchant-approved facts."""

import html
from typing import Annotated, Literal

from pydantic import Field

from .spec import Brief, StrictModel

Index = Annotated[int, Field(strict=True, ge=0)]


class CreativeChoice(StrictModel):
    lead_fact: Index
    supporting_facts: Annotated[list[Index], Field(min_length=0, max_length=7)]
    call_to_action: Literal["View product details", "See print details", "Explore the product"]
    hypothesis: Annotated[str, Field(min_length=1, max_length=240)]


def render_copy(brief: Brief, choice: CreativeChoice) -> dict:
    return render_from_facts(brief.product.facts, choice)


def render_from_facts(facts: list[str], choice: CreativeChoice) -> dict:
    if not 1 <= len(facts) <= 8 or any(
        not f.strip() or not f.isprintable() or len(f) > 180 for f in facts
    ):
        raise ValueError("supply up to eight short public catalog facts")
    indexes = [choice.lead_fact, *choice.supporting_facts]
    if len(set(indexes)) != len(indexes) or any(i >= len(facts) for i in indexes):
        raise ValueError("choose distinct fact indexes from this product's approved facts")
    if choice.call_to_action == "See print details" and not any(
        "print" in s.lower() for s in facts
    ):
        raise ValueError("print-specific CTA requires a print fact")
    return {
        "headline": facts[choice.lead_fact],
        "bullets": [facts[i] for i in choice.supporting_facts],
        "cta": choice.call_to_action,
        "internal_test_hypothesis": choice.hypothesis,
    }


def product_description(copy: dict) -> str:
    heading = "<p>" + html.escape(copy["headline"]) + "</p>"
    bullets = "".join(f"<li>{html.escape(fact)}</li>" for fact in copy["bullets"])
    return heading + ("<ul>" + bullets + "</ul>" if bullets else "")
