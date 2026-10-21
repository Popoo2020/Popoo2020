"""Synthetic model-output boundary; NO AI provider or network calls.

Shows how untrusted model suggestions would be constrained before a deterministic
policy engine. The mock is invented in 2026, not the original OpenAI prompts.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from demo.engine import Event

TASKS = {"inventory": "stock_check", "shift_gap": "shift_coverage", "complaint": "customer_follow_up"}

@dataclass(frozen=True)
class ModelProposal:
    event_id: str
    site: str
    task: str

def mock_model_output(event: Event) -> dict[str, str]:
    """Invented model-like output, not an AI inference or historical transcript."""
    return {"event_id": event.event_id, "site": event.site, "task": TASKS[event.kind]}

def validate_model_output(event: Event, raw: dict[str, Any]) -> ModelProposal:
    """Reject arbitrary commands, mismatched sites and unauthorised task types."""
    if not isinstance(raw, dict) or set(raw) != {"event_id", "site", "task"}:
        raise ValueError("Model output schema rejected")
    if any(not isinstance(raw[key], str) for key in ("event_id", "site", "task")):
        raise ValueError("Model output type rejected")
    if raw["event_id"] != event.event_id or raw["site"] != event.site:
        raise ValueError("Model output context mismatch")
    if raw["task"] != TASKS[event.kind]:
        raise ValueError("Model task outside authorised event scope")
    return ModelProposal(event.event_id, event.site, raw["task"])
