"""Adversarial regressions for the local simulator's authorization boundaries.

The fixture is independent of the bundled demo. These tests exercise outcomes,
not implementation details: an expired or unapproved identity must not gain an
assignment, and simulation must not manufacture fresh observation evidence.
"""

import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from identity_governance.common import digest, read_json
from identity_governance.engine import demo_approvals, make_plan, simulate


def scenario_fixture():
    """Two people, one incompatible role change, and two separate approvers."""
    entitlements = {}
    for entitlement, permission in (("old", "SalesWrite"), ("new", "FinanceApprove")):
        entitlements[entitlement] = {
            "provider": "aws",
            "resource": "synthetic-account",
            "permission": permission,
            "owner": "resource-owner",
            "authority": "provider",
            "label": permission,
        }
    identities = {}
    for subject, role in (("person-a", "finance"), ("person-b", "sales")):
        identities[subject] = {
            "kind": "employee",
            "status": "active",
            "role": role,
            "manager": "manager",
            "external_ids": {
                "azure": f"entra-{subject}",
                "aws": f"aws-{subject}",
                "gcp": f"gcp-{subject}",
            },
        }
    return {
        "schema_version": 1,
        "as_of": "2026-11-26T12:00:00Z",
        "policy": {
            "approvers": ["manager", "resource-owner"],
            "entitlements": entitlements,
            "roles": {"sales": ["old"], "finance": ["new"]},
            "conflicts": [["old", "new"]],
            "snapshot_max_age_minutes": 60,
            "plan_valid_minutes": 30,
        },
        "identities": identities,
        "snapshot": {
            "schema_version": 1,
            "scope": "catalogued_direct_assignments",
            "complete": {"azure": True, "aws": True, "gcp": True},
            "subjects": ["person-a", "person-b"],
            "captured_at": "2026-11-26T12:00:00Z",
            "assignments": [
                {"subject_id": "person-a", "entitlement_id": "old"},
                {"subject_id": "person-b", "entitlement_id": "old"},
            ],
            "disabled_subjects": [],
        },
        "events": {
            "mover": {
                "event_id": "move-a-001",
                "kind": "mover",
                "source": "authoritative_hr_fixture",
                "subject_id": "person-a",
                "effective_at": "2026-11-26T12:00:00Z",
                "target_role": "finance",
            },
            "review-b": {
                "event_id": "review-b-001",
                "kind": "access_review",
                "source": "authoritative_hr_fixture",
                "subject_id": "person-b",
                "effective_at": "2026-11-26T12:00:00Z",
            },
        },
    }


class AuthorizationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.scenario = scenario_fixture()

    def assert_no_grant(self, scenario, plan, approvals):
        """Both whole-input rejection and a blocked grant fail closed."""
        try:
            result = simulate(scenario, plan, approvals)
        except ValueError:
            return
        self.assertFalse(
            any(
                operation["action"] == "grant" and operation["status"] == "simulated"
                for operation in result["operations"]
            )
        )
        self.assertNotIn(
            {"subject_id": "person-a", "entitlement_id": "new"}, result["after"]["assignments"]
        )

    def test_control_fixture_allows_only_the_approved_role_change(self):
        plan = make_plan(self.scenario, "mover")
        result = simulate(self.scenario, plan, demo_approvals(plan))
        self.assertEqual(result["status"], "completed_simulation")
        self.assertEqual(
            result["after"]["assignments"],
            [
                {"subject_id": "person-a", "entitlement_id": "new"},
                {"subject_id": "person-b", "entitlement_id": "old"},
            ],
        )

    def test_recomputed_hash_cannot_authorize_a_forged_permission(self):
        plan = make_plan(self.scenario, "mover")
        next(item for item in plan["operations"] if item["action"] == "grant")["permission"] = (
            "AdministratorAccess"
        )
        plan["plan_id"] = digest({key: value for key, value in plan.items() if key != "plan_id"})
        with self.assertRaises(ValueError):
            simulate(self.scenario, plan, demo_approvals(plan))

    def test_old_approval_cannot_be_replayed_for_a_new_plan(self):
        first_plan = make_plan(self.scenario, "mover")
        approvals = demo_approvals(first_plan)
        later = deepcopy(self.scenario)
        later["as_of"] = "2026-11-26T12:01:00Z"
        second_plan = make_plan(later, "mover")
        self.assertNotEqual(first_plan["plan_id"], second_plan["plan_id"])
        self.assert_no_grant(later, second_plan, approvals)

    def test_explicit_denial_and_duplicate_approval_cannot_grant(self):
        plan = make_plan(self.scenario, "mover")
        for denial in (True, False):
            with self.subTest(explicit_denial=denial):
                approvals = demo_approvals(plan)
                if denial:
                    approvals[0]["decision"] = "deny"
                else:
                    approvals.append(deepcopy(approvals[0]))
                self.assert_no_grant(self.scenario, plan, approvals)

    def test_approval_expiry_is_exclusive(self):
        plan = make_plan(self.scenario, "mover")
        approvals = demo_approvals(plan)
        for approval in approvals:
            approval["expires_at"] = "2026-11-26T12:05:00Z"
        later = deepcopy(self.scenario)
        later["as_of"] = "2026-11-26T12:05:00Z"
        self.assert_no_grant(later, plan, approvals)

    def test_self_approval_as_manager_or_owner_never_grants(self):
        for role in ("manager", "owner"):
            with self.subTest(role=role):
                scenario = deepcopy(self.scenario)
                scenario["policy"]["approvers"].append("person-a")
                if role == "manager":
                    scenario["identities"]["person-a"]["manager"] = "person-a"
                else:
                    scenario["policy"]["entitlements"]["new"]["owner"] = "person-a"
                try:
                    plan = make_plan(scenario, "mover")
                except ValueError:
                    continue
                self.assert_no_grant(scenario, plan, demo_approvals(plan))

    def test_one_person_cannot_supply_both_required_approval_roles(self):
        self.scenario["policy"]["entitlements"]["new"]["owner"] = "manager"
        try:
            plan = make_plan(self.scenario, "mover")
        except ValueError:
            return
        self.assert_no_grant(self.scenario, plan, demo_approvals(plan))

    def test_unknown_approval_fields_and_non_demo_source_fail_closed(self):
        plan = make_plan(self.scenario, "mover")
        for extra in ({"force_approval": True}, {"source": "external_authenticated_user"}):
            with self.subTest(extra=extra):
                approvals = demo_approvals(plan)
                approvals[0].update(extra)
                self.assert_no_grant(self.scenario, plan, approvals)

    def test_failed_removal_preserves_other_removals_and_freezes_grants(self):
        policy = self.scenario["policy"]
        policy["entitlements"]["old-second"] = {
            **policy["entitlements"]["old"],
            "permission": "LegacyExport",
        }
        self.scenario["snapshot"]["assignments"].append(
            {"subject_id": "person-a", "entitlement_id": "old-second"}
        )
        plan = make_plan(self.scenario, "mover")
        failure = next(
            item["operation_id"]
            for item in plan["operations"]
            if item["entitlement_id"] == "old-second"
        )
        result = simulate(self.scenario, plan, demo_approvals(plan), fail_operations={failure})
        assignments = result["after"]["assignments"]
        self.assertNotIn({"subject_id": "person-a", "entitlement_id": "old"}, assignments)
        self.assertIn({"subject_id": "person-a", "entitlement_id": "old-second"}, assignments)
        self.assertNotIn({"subject_id": "person-a", "entitlement_id": "new"}, assignments)
        self.assertEqual(result["status"], "partial_simulation")

    def test_result_replay_is_deterministic_and_inputs_are_unchanged(self):
        plan = make_plan(self.scenario, "mover")
        approvals = demo_approvals(plan)
        original = deepcopy((self.scenario, plan, approvals))
        first = simulate(self.scenario, plan, approvals)
        second = simulate(self.scenario, plan, approvals)
        self.assertEqual(first, second)
        self.assertEqual((self.scenario, plan, approvals), original)
        with self.assertRaises(ValueError):
            simulate(self.scenario, plan, approvals, snapshot=first["after"])
        reconciled = make_plan(self.scenario, "mover", snapshot=first["after"])
        self.assertEqual(reconciled["operations"], [])


class ObservationAndTimeBoundaryTests(unittest.TestCase):
    def test_noop_review_cannot_certify_a_pre_expiry_target_after_expiry(self):
        scenario = scenario_fixture()
        scenario["identities"]["person-b"].update(kind="contractor", end_at="2026-11-26T12:05:00Z")
        plan = make_plan(scenario, "review-b")
        self.assertEqual(plan["operations"], [])
        scenario["as_of"] = "2026-11-26T12:10:00Z"
        with self.assertRaises(ValueError):
            simulate(scenario, plan, [])

        # Replanning after expiry must still allow the necessary containment.
        expired_plan = make_plan(scenario, "review-b")
        result = simulate(scenario, expired_plan, [])
        self.assertIn("person-b", result["after"]["disabled_subjects"])
        self.assertFalse(
            any(item["subject_id"] == "person-b" for item in result["after"]["assignments"])
        )

    def test_contractor_expiring_after_plan_cannot_receive_a_grant(self):
        scenario = scenario_fixture()
        identity = scenario["identities"]["person-a"]
        identity.update(kind="contractor", end_at="2026-11-26T12:05:00Z")
        plan = make_plan(scenario, "mover")
        approvals = demo_approvals(plan)
        scenario["as_of"] = "2026-11-26T12:10:00Z"
        with self.assertRaises(ValueError):
            simulate(scenario, plan, approvals)

    def test_simulation_does_not_refresh_an_untouched_person_observation(self):
        scenario = scenario_fixture()
        scenario["policy"]["snapshot_max_age_minutes"] = 30
        scenario["as_of"] = "2026-11-26T12:29:00Z"
        plan = make_plan(scenario, "mover")
        result = simulate(scenario, plan, demo_approvals(plan))
        self.assertEqual(result["after"]["captured_at"], scenario["snapshot"]["captured_at"])
        scenario["as_of"] = "2026-11-26T12:58:00Z"
        with self.assertRaises(ValueError):
            make_plan(scenario, "review-b", snapshot=result["after"])

    def test_partial_snapshot_and_truthy_completeness_cannot_create_plan(self):
        for complete in (
            {"azure": True, "aws": True},
            {"azure": True, "aws": False, "gcp": True},
            {"azure": True, "aws": 1, "gcp": True},
            {"azure": True, "aws": "true", "gcp": True},
        ):
            with self.subTest(complete=complete):
                scenario = scenario_fixture()
                scenario["snapshot"]["complete"] = complete
                with self.assertRaises(ValueError):
                    make_plan(scenario, "mover")

    def test_expired_plan_is_rejected_at_its_exact_expiry(self):
        scenario = scenario_fixture()
        plan = make_plan(scenario, "mover")
        scenario["as_of"] = plan["expires_at"]
        with self.assertRaises(ValueError):
            simulate(scenario, plan, demo_approvals(plan))


class InputBoundaryTests(unittest.TestCase):
    def test_wrong_container_and_identifier_types_raise_validation_errors(self):
        for field in ("policy", "approver", "role", "provider", "kind", "complete"):
            with self.subTest(field=field):
                scenario = scenario_fixture()
                if field == "policy":
                    scenario["policy"] = None
                elif field == "approver":
                    scenario["policy"]["approvers"] = [{}]
                elif field == "role":
                    scenario["policy"]["roles"]["finance"] = [{}]
                elif field == "provider":
                    scenario["policy"]["entitlements"]["new"]["provider"] = []
                elif field == "kind":
                    scenario["identities"]["person-a"]["kind"] = []
                else:
                    scenario["snapshot"]["complete"] = ["azure", "aws", "gcp"]
                with self.assertRaises(ValueError):
                    make_plan(scenario, "mover")

    def test_schema_version_must_be_an_integer_not_an_equal_bool_or_float(self):
        for location in ("scenario", "snapshot"):
            for version in (True, 1.0):
                with self.subTest(location=location, version=version):
                    scenario = scenario_fixture()
                    target = scenario if location == "scenario" else scenario["snapshot"]
                    target["schema_version"] = version
                    with self.assertRaises(ValueError):
                        make_plan(scenario, "mover")

    def test_unknown_security_semantics_are_rejected_not_silently_ignored(self):
        for location, field in (
            ("scenario", "live_execution"),
            ("policy", "approvals_optional"),
            ("identity", "suspended"),
            ("entitlement", "bypass_owner_approval"),
            ("event", "skip_access_review"),
            ("snapshot", "inherited_access_unresolved"),
        ):
            with self.subTest(location=location):
                scenario = scenario_fixture()
                targets = {
                    "scenario": scenario,
                    "policy": scenario["policy"],
                    "identity": scenario["identities"]["person-a"],
                    "entitlement": scenario["policy"]["entitlements"]["new"],
                    "event": scenario["events"]["mover"],
                    "snapshot": scenario["snapshot"],
                }
                targets[location][field] = True
                with self.assertRaises(ValueError):
                    make_plan(scenario, "mover")

    def test_json_rejects_duplicate_keys_constants_and_exponent_overflow(self):
        documents = (
            '{"policy":{"approve":true,"approve":false}}',
            '{"amount":NaN}',
            '{"amount":Infinity}',
            '{"amount":1e999}',
            '{"amount":-1e999}',
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "untrusted.json"
            for document in documents:
                with self.subTest(document=document):
                    path.write_text(document, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        read_json(path)


if __name__ == "__main__":
    unittest.main()
