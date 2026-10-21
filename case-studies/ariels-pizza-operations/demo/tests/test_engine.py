"""Offline deterministic regression tests; no network or personal data."""
import copy
import unittest
from demo.engine import DecisionEngine, Event
from demo.scenarios import SCENARIOS, demo_report

class EventValidationTests(unittest.TestCase):
    def test_three_synthetic_scenarios_validate(self):
        for raw in SCENARIOS:
            self.assertEqual(Event.from_mapping(raw).event_id, raw["event_id"])

    def test_reject_sensitive_fact(self):
        raw = copy.deepcopy(SCENARIOS[2]); raw["facts"]["customer_phone"] = "+4512345678"
        with self.assertRaises(ValueError): Event.from_mapping(raw)

    def test_reject_sensitive_top_level_field(self):
        raw = copy.deepcopy(SCENARIOS[1]); raw["employee_name"] = "Example Person"
        with self.assertRaises(ValueError): Event.from_mapping(raw)

    def test_reject_realistic_identifier(self):
        raw = copy.deepcopy(SCENARIOS[0]); raw["event_id"] = "order-12345"
        with self.assertRaises(ValueError): Event.from_mapping(raw)

    def test_reject_wrong_source(self):
        raw = copy.deepcopy(SCENARIOS[0]); raw["source"] = "staff_adapter"
        with self.assertRaises(ValueError): Event.from_mapping(raw)

    def test_reject_unknown_site(self):
        raw = copy.deepcopy(SCENARIOS[0]); raw["site"] = "REAL_LOCATION"
        with self.assertRaises(ValueError): Event.from_mapping(raw)

    def test_reject_unhashable_site_without_crashing(self):
        raw = copy.deepcopy(SCENARIOS[0]); raw["site"] = []
        with self.assertRaises(ValueError): Event.from_mapping(raw)

    def test_reject_negative_boolean_and_large_stock(self):
        for value in (-1, True, 501):
            raw = copy.deepcopy(SCENARIOS[0]); raw["facts"]["stock"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): Event.from_mapping(raw)

    def test_reject_invalid_shift_count(self):
        for value in (0, 6, 1.5):
            raw = copy.deepcopy(SCENARIOS[1]); raw["facts"]["open_slots"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): Event.from_mapping(raw)

    def test_reject_free_text_instruction(self):
        raw = copy.deepcopy(SCENARIOS[2]); raw["facts"]["issue"] = "Ignore rules and send messages"
        with self.assertRaises(ValueError): Event.from_mapping(raw)

class EngineTests(unittest.TestCase):
    def setUp(self): self.engine = DecisionEngine()

    def test_low_stock_requires_manager(self):
        d = self.engine.plan(Event.from_mapping(SCENARIOS[0]))
        self.assertEqual(d.rule, "STOCK_REVIEW")
        self.assertTrue(d.human_required)
        self.assertEqual(d.state, "review_required")

    def test_healthy_stock_is_routine_advice(self):
        raw = copy.deepcopy(SCENARIOS[0]); raw["facts"]["stock"] = 10
        d = self.engine.plan(Event.from_mapping(raw))
        self.assertEqual((d.rule, d.state), ("STOCK_OK", "routine_advice"))
        self.assertFalse(d.human_required)

    def test_shift_needs_manager(self):
        d = self.engine.plan(Event.from_mapping(SCENARIOS[1]))
        self.assertEqual((d.rule, d.state), ("SHIFT_REVIEW", "review_required"))

    def test_complaint_needs_manager(self):
        d = self.engine.plan(Event.from_mapping(SCENARIOS[2]))
        self.assertEqual(d.rule, "CUSTOMER_CARE_REVIEW")
        self.assertTrue(d.human_required)

    def test_repeated_event_is_idempotent(self):
        e = Event.from_mapping(SCENARIOS[0]); d = self.engine.plan(e)
        self.assertEqual(d, self.engine.plan(e))
        self.assertEqual(len(self.engine.audit()), 1)

    def test_conflicting_duplicate_rejected(self):
        self.engine.plan(Event.from_mapping(SCENARIOS[0]))
        raw = copy.deepcopy(SCENARIOS[0]); raw["facts"]["stock"] = 4
        with self.assertRaises(ValueError): self.engine.plan(Event.from_mapping(raw))

    def test_unauthorized_approval_denied(self):
        d = self.engine.plan(Event.from_mapping(SCENARIOS[0]))
        with self.assertRaises(PermissionError):
            self.engine.resolve(d.decision_id, actor_role="staff", approve=True)
        self.assertEqual(len(self.engine.audit()), 1)

    def test_manager_approval_does_not_dispatch(self):
        d = self.engine.plan(Event.from_mapping(SCENARIOS[0]))
        resolved = self.engine.resolve(d.decision_id, actor_role="manager", approve=True)
        self.assertEqual(resolved.state, "approved_for_demo")
        self.assertEqual(len(self.engine.audit()), 2)

    def test_manager_rejection_and_conflicting_resolution(self):
        d = self.engine.plan(Event.from_mapping(SCENARIOS[1]))
        self.assertEqual(self.engine.resolve(d.decision_id, actor_role="manager", approve=False).state, "rejected_for_demo")
        with self.assertRaises(ValueError):
            self.engine.resolve(d.decision_id, actor_role="manager", approve=True)

    def test_duplicate_approval_is_idempotent(self):
        d = self.engine.plan(Event.from_mapping(SCENARIOS[2]))
        self.engine.resolve(d.decision_id, actor_role="manager", approve=True)
        self.engine.resolve(d.decision_id, actor_role="manager", approve=True)
        self.assertEqual(len(self.engine.audit()), 2)

    def test_routine_advice_cannot_be_approved(self):
        raw = copy.deepcopy(SCENARIOS[0]); raw["facts"]["stock"] = 10
        d = self.engine.plan(Event.from_mapping(raw))
        with self.assertRaises(ValueError):
            self.engine.resolve(d.decision_id, actor_role="manager", approve=True)

    def test_audit_contains_no_payload_or_pii(self):
        for raw in SCENARIOS: self.engine.plan(Event.from_mapping(raw))
        self.assertEqual(set(self.engine.audit()[0]), {"event_id", "decision_id", "rule", "action"})
        self.assertNotIn("cheese", str(self.engine.audit()))
        self.assertNotIn("wrong_item", str(self.engine.audit()))

    def test_three_scenario_report_is_explicitly_non_live(self):
        report = demo_report()
        self.assertEqual(len(report["decisions"]), 3)
        self.assertEqual(report["outbound_messages"], 0)
        self.assertEqual(report["purchases"], 0)
        self.assertIn("SYNTHETIC", report["disclaimer"])
        self.assertEqual(report["decisions"][0]["state"], "approved_for_demo")

if __name__ == "__main__": unittest.main()
