"""Independent 2026 portfolio demo, NOT historical Ariel's Pizza source.

Purely local decision support: no network, provider SDKs, employee/customer
records, external messages or purchasing.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from hashlib import sha256
import re
from typing import Any

SITES = frozenset({"SITE_A", "SITE_B", "SITE_C"})
SOURCES = {"inventory": "ordering_adapter", "shift_gap": "staff_adapter", "complaint": "ordering_adapter"}
FIELDS = {"inventory": {"item", "stock", "reorder_point"}, "shift_gap": {"role", "open_slots"}, "complaint": {"issue", "severity"}}
ENUMS = {"item": {"dough", "cheese", "boxes"}, "role": {"kitchen", "delivery", "front_of_house"}, "issue": {"late_order", "wrong_item", "quality_issue"}, "severity": {"low", "high"}}
EVENT_ID = re.compile(r"^demo-[a-z0-9-]{3,40}$")

@dataclass(frozen=True)
class Event:
    event_id: str
    kind: str
    site: str
    source: str
    facts: dict[str, str | int]

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> Event:
        """Fail closed on unexpected fields, accepting only aggregate synthetic facts."""
        if not isinstance(raw, dict) or set(raw) != {"event_id", "kind", "site", "source", "facts"}:
            raise ValueError("Event schema rejected")
        event_id, kind, site, source, facts = (raw[k] for k in ("event_id", "kind", "site", "source", "facts"))
        if not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id):
            raise ValueError("Event identifier must be synthetic")
        if (not isinstance(kind, str) or kind not in SOURCES
                or not isinstance(site, str) or site not in SITES
                or not isinstance(source, str) or source != SOURCES[kind]):
            raise ValueError("Event routing rejected")
        if not isinstance(facts, dict) or set(facts) != FIELDS[kind]:
            raise ValueError("Facts schema rejected: personal or unexpected data are not accepted")
        for key, value in facts.items():
            if key in ENUMS and (not isinstance(value, str) or value not in ENUMS[key]):
                raise ValueError("Unsupported categorical fact")
            if key in {"stock", "reorder_point", "open_slots"} and (type(value) is not int or not 0 <= value <= 500):
                raise ValueError("Numeric fact outside permitted range")
        if kind == "shift_gap" and not 1 <= facts["open_slots"] <= 5:
            raise ValueError("Shift slots outside permitted range")
        if kind == "inventory" and facts["reorder_point"] == 0:
            raise ValueError("Reorder threshold must be positive")
        return cls(event_id, kind, site, source, dict(facts))

@dataclass(frozen=True)
class Decision:
    decision_id: str
    event_id: str
    site: str
    kind: str
    rule: str
    recommendation: str
    state: str
    human_required: bool

    def as_dict(self) -> dict[str, str | bool]:
        return vars(self).copy()

class DecisionEngine:
    """In-memory idempotent advice; approvals never dispatch external actions."""
    def __init__(self) -> None:
        self._decisions: dict[str, Decision] = {}
        self._events: dict[str, Event] = {}
        self._audit: list[dict[str, str]] = []

    def plan(self, event: Event) -> Decision:
        if not isinstance(event, Event):
            raise TypeError("Validated Event required")
        event = Event.from_mapping(vars(event))  # Prevent manual dataclass bypass.
        if event.event_id in self._events:
            if self._events[event.event_id] != event:
                raise ValueError("Conflicting event identifier")
            return self._decisions[event.event_id]
        digest = sha256(event.event_id.encode("ascii")).hexdigest()[:12]
        facts = event.facts
        if event.kind == "inventory":
            low = facts["stock"] < facts["reorder_point"]
            rule = "STOCK_REVIEW" if low else "STOCK_OK"
            recommendation = (
                f"Review stock and potential replenishment of {facts['item']} at {event.site} "
                f"(count {facts['stock']}; threshold {facts['reorder_point']})."
                if low else f"No replenishment suggestion for {facts['item']} at {event.site}."
            )
            human_required = low
        elif event.kind == "shift_gap":
            rule = "SHIFT_REVIEW"
            recommendation = f"Manager to review voluntary {facts['role']} coverage for {facts['open_slots']} open slot(s) at {event.site}."
            human_required = True
        else:
            rule = "CUSTOMER_CARE_REVIEW"
            recommendation = f"Manager to review {facts['severity']} priority {facts['issue']} customer-service follow-up at {event.site}."
            human_required = True
        decision = Decision(f"decision-{digest}", event.event_id, event.site, event.kind, rule,
                            recommendation, "review_required" if human_required else "routine_advice", human_required)
        self._events[event.event_id] = event
        self._decisions[event.event_id] = decision
        self._audit.append({"event_id": event.event_id, "decision_id": decision.decision_id, "rule": rule, "action": "planned"})
        return decision

    def resolve(self, decision_id: str, *, actor_role: str, approve: bool) -> Decision:
        """Approve/reject a demo advisory decision; never send a real task."""
        if actor_role != "manager" or type(approve) is not bool:
            raise PermissionError("Only an explicit manager decision is accepted")
        match = next((d for d in self._decisions.values() if d.decision_id == decision_id), None)
        if match is None or not match.human_required:
            raise ValueError("Unknown or non-reviewable decision")
        target = "approved_for_demo" if approve else "rejected_for_demo"
        if match.state == target:
            return match
        if match.state != "review_required":
            raise ValueError("Conflicting decision resolution")
        updated = replace(match, state=target)
        self._decisions[match.event_id] = updated
        self._audit.append({"event_id": match.event_id, "decision_id": match.decision_id, "rule": match.rule, "action": target})
        return updated

    def audit(self) -> tuple[dict[str, str], ...]:
        """Only synthetic identifiers and rule codes, never source payloads."""
        return tuple(dict(row) for row in self._audit)
