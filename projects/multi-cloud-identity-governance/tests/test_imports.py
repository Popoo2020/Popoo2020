"""Provider exports must establish bounded scope before they can feed a plan."""

import json
import unittest
from copy import deepcopy
from pathlib import Path

from identity_governance.common import digest
from identity_governance.engine import make_plan, validate_snapshot
from identity_governance.imports import snapshot_from_exports

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def read_example(name):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


class ImportPipelineTests(unittest.TestCase):
    def setUp(self):
        self.scenario = read_example("scenario.json")
        self.exports = read_example("export-bundle.json")
        self.captured_at = "2026-11-26T08:55:00Z"

    def import_snapshot(self):
        return snapshot_from_exports(self.scenario, "emp-014", self.exports, self.captured_at)

    def test_exports_feed_the_real_mover_plan(self):
        result = self.import_snapshot()
        snapshot = result["snapshot"]
        validate_snapshot(self.scenario, snapshot, "emp-014", self.scenario["as_of"])
        self.assertEqual(snapshot["scope"], "catalogued_direct_assignments")
        self.assertEqual(snapshot["subjects"], ["emp-014"])
        self.assertEqual(snapshot["complete"], {"azure": True, "aws": True, "gcp": True})
        self.assertEqual(
            {entry["entitlement_id"] for entry in snapshot["assignments"]},
            {"azure.staff", "azure.order_ops", "aws.order_operator", "gcp.sales_viewer"},
        )
        plan = make_plan(self.scenario, "mover", snapshot)
        self.assertEqual(
            {
                (operation["action"], operation["entitlement_id"])
                for operation in plan["operations"]
            },
            {
                ("revoke", "azure.order_ops"),
                ("revoke", "aws.order_operator"),
                ("revoke", "gcp.sales_viewer"),
                ("grant", "azure.finance"),
                ("grant", "aws.cost_reader"),
                ("grant", "gcp.finance_viewer"),
            },
        )
        self.assertEqual(plan["operations"], make_plan(self.scenario, "mover")["operations"])
        self.assertEqual(plan["snapshot_digest"], digest(snapshot))

    def test_fixture_documents_stay_aligned_with_individual_examples(self):
        for provider, filename in (
            ("azure", "azure_direct_groups.json"),
            ("aws", "aws_direct_assignments.json"),
            ("gcp", "gcp_direct_policy.json"),
        ):
            with self.subTest(provider=provider):
                self.assertEqual(
                    self.exports["documents"][provider][0], read_example(f"providers/{filename}")
                )
        self.assertEqual(len(self.exports["coverage"]), 5)
        self.assertEqual(len(self.scenario["policy"]["entitlements"]), 9)

    def test_provenance_is_separate_resolvable_and_explicit_about_limits(self):
        result = self.import_snapshot()
        snapshot, evidence = result["snapshot"], result["evidence"]
        self.assertEqual(
            set(snapshot),
            {
                "schema_version",
                "captured_at",
                "scope",
                "complete",
                "subjects",
                "disabled_subjects",
                "assignments",
            },
        )
        self.assertTrue(
            all(
                set(assignment) == {"subject_id", "entitlement_id"}
                for assignment in snapshot["assignments"]
            )
        )
        self.assertEqual(evidence["snapshot_digest"], digest(snapshot))
        self.assertEqual(evidence["exports_digest"], digest(self.exports))
        self.assertEqual(len(evidence["coverage"]), 5)
        self.assertEqual(len(evidence["assignments"]), 4)
        self.assertIs(evidence["source_authenticated"], False)
        self.assertIs(evidence["actual_collection_completeness_verified"], False)
        self.assertTrue(any("disabled_subjects=[]" in note for note in evidence["assumptions"]))
        for assignment in evidence["assignments"]:
            target = self.exports
            for segment in assignment["export_ref"].strip("/").split("/"):
                target = target[int(segment)] if isinstance(target, list) else target[segment]
            self.assertIsNotNone(target)
            self.assertIn("#", assignment["source_ref"])

    def test_import_does_not_mutate_inputs_and_is_deterministic(self):
        original_scenario, original_exports = deepcopy(self.scenario), deepcopy(self.exports)
        first = self.import_snapshot()
        self.assertEqual(first, self.import_snapshot())
        self.assertEqual(self.scenario, original_scenario)
        self.assertEqual(self.exports, original_exports)
        first["evidence"]["coverage"][0]["resource"] = "changed-output-only"
        self.assertEqual(self.exports, original_exports)

    def test_every_provider_is_required_with_a_nonempty_document_list(self):
        for provider in ("azure", "aws", "gcp"):
            for mode in ("missing", "empty"):
                with self.subTest(provider=provider, mode=mode):
                    exports = deepcopy(self.exports)
                    if mode == "missing":
                        del exports["documents"][provider]
                    else:
                        exports["documents"][provider] = []
                    with self.assertRaises(ValueError):
                        snapshot_from_exports(self.scenario, "emp-014", exports, self.captured_at)

    def test_empty_results_still_require_the_correct_immutable_subject(self):
        for provider in ("azure", "aws", "gcp"):
            with self.subTest(provider=provider):
                exports = deepcopy(self.exports)
                document = exports["documents"][provider][0]
                document["principal_id"] = self.scenario["identities"]["emp-015"]["external_ids"][
                    provider
                ]
                if provider == "azure":
                    document["groups"] = {"value": []}
                elif provider == "aws":
                    document["response"] = {"AccountAssignments": []}
                else:
                    document["policy"]["bindings"] = []
                with self.assertRaisesRegex(ValueError, "immutable external identity"):
                    snapshot_from_exports(self.scenario, "emp-014", exports, self.captured_at)

    def test_aws_empty_queries_need_explicit_coverage_for_every_catalogued_permission(self):
        self.exports["coverage"] = [
            row
            for row in self.exports["coverage"]
            if row.get("document_index") != 1 or row["provider"] != "aws"
        ]
        with self.assertRaisesRegex(ValueError, "Incomplete catalogue coverage"):
            self.import_snapshot()

    def test_empty_responses_do_not_allow_one_aws_query_to_cover_all_permissions(self):
        for document in self.exports["documents"]["aws"]:
            document["response"] = {"AccountAssignments": []}
        for row in self.exports["coverage"]:
            if row["provider"] == "aws":
                row["document_index"] = 0
        with self.assertRaisesRegex(ValueError, "multiple query scopes"):
            self.import_snapshot()

    def test_aws_coverage_cannot_contradict_non_subject_response_rows(self):
        assignments = self.exports["documents"]["aws"][0]["response"]["AccountAssignments"]
        for assignment in assignments:
            assignment["PrincipalId"] = "99999999-9999-4999-8999-999999999999"
            assignment["PermissionSetArn"] = (
                "arn:aws:sso:::permissionSet/ssoins-0123456789abcdef/ps-fedcba9876543210"
            )
        with self.assertRaisesRegex(ValueError, "coverage contradicts"):
            self.import_snapshot()

    def test_catalogued_permissions_outside_the_target_role_still_need_coverage(self):
        del self.exports["documents"]["aws"][2]
        self.exports["coverage"] = [
            row
            for row in self.exports["coverage"]
            if row["provider"] != "aws" or row["document_index"] != 2
        ]
        # support_reader is not part of emp-014's old or desired role. Excluding
        # it would nevertheless hide an existing out-of-role assignment.
        with self.assertRaisesRegex(ValueError, "Incomplete catalogue coverage"):
            self.import_snapshot()

    def test_partial_or_missing_coverage_is_never_inferred_from_present_records(self):
        for complete in (False, None, 1, "true"):
            with self.subTest(complete=complete):
                exports = deepcopy(self.exports)
                exports["coverage"][0]["complete"] = complete
                with self.assertRaisesRegex(ValueError, "complete=true"):
                    snapshot_from_exports(self.scenario, "emp-014", exports, self.captured_at)
        del self.exports["coverage"]
        with self.assertRaises(ValueError):
            self.import_snapshot()

    def test_duplicate_scopes_and_uncovered_documents_are_rejected(self):
        duplicated = deepcopy(self.exports)
        duplicated["documents"]["azure"].append(deepcopy(duplicated["documents"]["azure"][0]))
        extra_claim = deepcopy(duplicated["coverage"][0])
        extra_claim["document_index"] = 1
        duplicated["coverage"].append(extra_claim)
        with self.assertRaisesRegex(ValueError, "Duplicate provider query scope"):
            snapshot_from_exports(self.scenario, "emp-014", duplicated, self.captured_at)
        duplicated["coverage"].pop()
        with self.assertRaisesRegex(ValueError, "Every supplied provider document"):
            snapshot_from_exports(self.scenario, "emp-014", duplicated, self.captured_at)

    def test_unknown_observed_assignment_is_rejected_instead_of_discarded(self):
        for provider in ("azure", "gcp"):
            with self.subTest(provider=provider):
                exports = deepcopy(self.exports)
                if provider == "azure":
                    exports["documents"][provider][0]["groups"]["value"][0]["id"] = (
                        "66666666-6666-4666-8666-666666666666"
                    )
                else:
                    exports["documents"][provider][0]["policy"]["bindings"][0]["role"] = (
                        "roles/storage.objectViewer"
                    )
                with self.assertRaisesRegex(ValueError, "no catalogue mapping"):
                    snapshot_from_exports(self.scenario, "emp-014", exports, self.captured_at)

    def test_unknown_scope_and_wrong_document_resource_are_rejected(self):
        self.exports["coverage"][0]["resource"] = "unknown-tenant"
        with self.assertRaisesRegex(ValueError, "outside the entitlement catalogue"):
            self.import_snapshot()
        self.exports = read_example("export-bundle.json")
        self.exports["documents"]["azure"][0]["tenant_id"] = "wrong-tenant"
        with self.assertRaisesRegex(ValueError, "does not match its provider document"):
            self.import_snapshot()

    def test_adapter_failures_are_not_bypassed_by_complete_assertion(self):
        self.exports["documents"]["aws"][2]["response"]["NextToken"] = "more-data"
        with self.assertRaisesRegex(ValueError, "incomplete pagination"):
            self.import_snapshot()
        self.exports = read_example("export-bundle.json")
        self.exports["documents"]["gcp"][0]["policy"]["bindings"][0]["condition"] = {
            "expression": "true"
        }
        with self.assertRaisesRegex(ValueError, "conditional"):
            self.import_snapshot()

    def test_an_empty_but_explicitly_covered_snapshot_is_valid(self):
        self.exports["documents"]["azure"][0]["groups"] = {"value": []}
        for document in self.exports["documents"]["aws"]:
            document["response"] = {"AccountAssignments": []}
        self.exports["documents"]["gcp"][0]["policy"]["bindings"] = []
        result = self.import_snapshot()
        self.assertEqual(result["snapshot"]["assignments"], [])
        self.assertEqual(result["evidence"]["assignments"], [])
        self.assertEqual(len(result["evidence"]["coverage"]), 5)

    def test_stale_future_and_naive_capture_times_cannot_feed_planning(self):
        for captured_at in ("2026-11-26T06:00:00Z", "2026-11-26T10:00:00Z", "2026-11-26T08:55:00"):
            with self.subTest(captured_at=captured_at):
                with self.assertRaises(ValueError):
                    snapshot_from_exports(self.scenario, "emp-014", self.exports, captured_at)

    def test_unknown_subject_or_ambiguous_catalogue_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not mapped"):
            snapshot_from_exports(self.scenario, "emp-unknown", self.exports, self.captured_at)
        self.scenario["policy"]["entitlements"]["azure.duplicate"] = deepcopy(
            self.scenario["policy"]["entitlements"]["azure.staff"]
        )
        with self.assertRaisesRegex(ValueError, "Duplicate provider/resource/permission"):
            self.import_snapshot()

    def test_malformed_bundle_and_query_metadata_raise_value_error(self):
        for schema_version in (True, "1", 2):
            with self.subTest(schema_version=schema_version):
                exports = deepcopy(self.exports)
                exports["schema_version"] = schema_version
                with self.assertRaises(ValueError):
                    snapshot_from_exports(self.scenario, "emp-014", exports, self.captured_at)
        for index in (True, -1, "0", 100):
            with self.subTest(index=index):
                exports = deepcopy(self.exports)
                exports["coverage"][0]["document_index"] = index
                with self.assertRaises(ValueError):
                    snapshot_from_exports(self.scenario, "emp-014", exports, self.captured_at)
        self.exports["coverage"][1].pop("permission")
        with self.assertRaises(ValueError):
            self.import_snapshot()


if __name__ == "__main__":
    unittest.main()
