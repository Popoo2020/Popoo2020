"""Three invented offline scenarios. Run: python -m demo.scenarios."""
from __future__ import annotations
import json
from demo.engine import DecisionEngine, Event

# Invented counts and aliases; no historical staff, customer or order data.
SCENARIOS = [
    {"event_id": "demo-stock-001", "kind": "inventory", "site": "SITE_A", "source": "ordering_adapter", "facts": {"item": "cheese", "stock": 3, "reorder_point": 8}},
    {"event_id": "demo-shift-002", "kind": "shift_gap", "site": "SITE_B", "source": "staff_adapter", "facts": {"role": "kitchen", "open_slots": 1}},
    {"event_id": "demo-complaint-003", "kind": "complaint", "site": "SITE_C", "source": "ordering_adapter", "facts": {"issue": "wrong_item", "severity": "high"}},
]

def demo_report() -> dict[str, object]:
    engine = DecisionEngine()
    planned = [engine.plan(Event.from_mapping(raw)) for raw in SCENARIOS]
    # Synthetic approval in memory only. Nothing is sent or purchased.
    approved = engine.resolve(planned[0].decision_id, actor_role="manager", approve=True)
    return {
        "disclaimer": "SYNTHETIC OFFLINE DEMO — not historical source or a live integration",
        "decisions": [engine.plan(Event.from_mapping(raw)).as_dict() for raw in SCENARIOS],
        "manager_example": approved.as_dict(),
        "audit": list(engine.audit()),
        "outbound_messages": 0,
        "purchases": 0,
    }

def main() -> None:
    print(json.dumps(demo_report(), ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
