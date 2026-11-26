"""Business acceptance checks for the supplied workforce scenarios."""

import unittest
from copy import deepcopy
from pathlib import Path

from identity_governance.common import read_json
from identity_governance.engine import access_for, demo_approvals, make_plan, simulate

ROOT = Path(__file__).resolve().parents[1]


class WorkforceAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.scenario = read_json(ROOT / "examples/scenario.json")

    def test_mover_removes_old_access_before_granting_finance_access(self):
        plan = make_plan(self.scenario, "mover")
        result = simulate(self.scenario, plan, demo_approvals(plan))
        self.assertEqual(
            [op["action"] for op in result["operations"]], ["revoke"] * 3 + ["grant"] * 3
        )
        self.assertEqual(
            access_for(result["after"], "emp-014"),
            {
                "azure.staff",
                "azure.finance",
                "aws.cost_reader",
                "gcp.finance_viewer",
            },
        )
        self.assertEqual(result["status"], "completed_simulation")
        self.assertFalse(result["review"]["live_access_verified"])
        self.assertFalse(result["review"]["session_revocation_verified"])

    def test_joiner_receives_only_the_role_catalogue(self):
        plan = make_plan(self.scenario, "joiner")
        result = simulate(self.scenario, plan, demo_approvals(plan))
        self.assertEqual(
            access_for(result["after"], "emp-015"),
            set(self.scenario["policy"]["roles"]["order_operations"]),
        )
        self.assertEqual(access_for(result["before"], "emp-015"), set())

    def test_departure_and_expiry_disable_and_remove_assignments_in_the_model(self):
        for name, subject in (("leaver", "emp-019"), ("contractor-expiry", "contractor-007")):
            with self.subTest(name=name):
                plan = make_plan(self.scenario, name)
                result = simulate(self.scenario, plan, [])
                self.assertEqual(plan["operations"][0]["action"], "disable_identity")
                self.assertIn(subject, result["after"]["disabled_subjects"])
                self.assertEqual(access_for(result["after"], subject), set())
                self.assertEqual(result["status"], "completed_simulation")

    def test_access_review_removes_excess_but_does_not_provision_missing_access(self):
        plan = make_plan(self.scenario, "access-review")
        result = simulate(self.scenario, plan, [])
        self.assertEqual(access_for(result["after"], "emp-014"), {"azure.staff"})
        self.assertFalse(any(op["action"] == "grant" for op in plan["operations"]))
        self.assertEqual(len(result["review"]["missing_role_assignments"]), 3)
        self.assertFalse(result["review"]["catalogued_assignment_target_reached"])

    def test_missing_approval_never_prevents_policy_driven_removals(self):
        plan = make_plan(self.scenario, "mover")
        result = simulate(self.scenario, plan, [])
        self.assertEqual(result["status"], "partial_simulation")
        self.assertEqual(access_for(result["after"], "emp-014"), {"azure.staff"})
        self.assertEqual(sum(op["status"] == "blocked" for op in result["operations"]), 3)

    def test_failed_grant_is_reported_as_partial_and_requires_a_new_plan(self):
        plan = make_plan(self.scenario, "mover")
        failed = next(
            op["operation_id"]
            for op in plan["operations"]
            if op["entitlement_id"] == "aws.cost_reader"
        )
        result = simulate(self.scenario, plan, demo_approvals(plan), fail_operations={failed})
        self.assertEqual(result["status"], "partial_simulation")
        self.assertEqual(result["review"]["missing_role_assignments"], ["aws.cost_reader"])
        new_plan = make_plan(self.scenario, "mover", result["after"])
        self.assertEqual(len(new_plan["operations"]), 1)
        self.assertEqual(new_plan["operations"][0]["entitlement_id"], "aws.cost_reader")
        self.assertNotEqual(plan["plan_id"], new_plan["plan_id"])

    def test_new_plan_after_completed_move_has_no_duplicate_grants(self):
        plan = make_plan(self.scenario, "mover")
        result = simulate(self.scenario, plan, demo_approvals(plan))
        self.assertEqual(make_plan(self.scenario, "mover", result["after"])["operations"], [])

    def test_hr_role_and_lifecycle_status_must_agree_with_the_event(self):
        self.scenario["events"]["mover"]["target_role"] = "order_operations"
        with self.assertRaises(ValueError):
            make_plan(self.scenario, "mover")
        self.scenario["identities"]["emp-019"]["status"] = "active"
        with self.assertRaises(ValueError):
            make_plan(self.scenario, "leaver")

    def test_invalid_target_role_is_rejected_before_any_operation(self):
        self.scenario["policy"]["roles"]["finance_analyst"].append("aws.order_operator")
        with self.assertRaises(ValueError):
            make_plan(self.scenario, "mover")

    def test_role_change_does_not_alter_other_identities(self):
        plan = make_plan(self.scenario, "mover")
        result = simulate(self.scenario, plan, demo_approvals(plan))
        for subject in ("emp-015", "emp-019", "contractor-007"):
            self.assertEqual(
                access_for(result["before"], subject), access_for(result["after"], subject)
            )

    def test_changed_policy_or_workforce_record_invalidates_approval(self):
        plan = make_plan(self.scenario, "mover")
        for mutation in ("policy", "identity"):
            scenario = deepcopy(self.scenario)
            if mutation == "policy":
                scenario["policy"]["snapshot_max_age_minutes"] = 45
            else:
                scenario["identities"]["emp-014"]["manager"] = "manager-operations"
            with self.assertRaises(ValueError):
                simulate(scenario, plan, demo_approvals(plan))


if __name__ == "__main__":
    unittest.main()
