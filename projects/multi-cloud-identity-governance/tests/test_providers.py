"""Offline normalization boundaries, with synthetic provider-shaped snapshots."""

import json
import unittest
from copy import deepcopy
from pathlib import Path

from identity_governance.providers import normalize_aws, normalize_azure, normalize_gcp

FIXTURES = Path(__file__).resolve().parents[1] / "examples" / "providers"
OUTPUT_FIELDS = {"provider", "principal_id", "entitlement_id", "resource", "source_ref"}


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AzureAdapterTests(unittest.TestCase):
    def setUp(self):
        self.document = fixture("azure_direct_groups.json")

    def test_native_direct_groups_keep_ids_not_display_names(self):
        original = deepcopy(self.document)
        records = normalize_azure(self.document)
        self.assertEqual(len(records), 2)
        self.assertEqual(
            records[0],
            {
                "provider": "azure",
                "principal_id": self.document["principal_id"],
                "entitlement_id": "33333333-3333-4333-8333-333333333333",
                "resource": self.document["tenant_id"],
                "source_ref": (
                    "azure:00000000-0000-4000-8000-000000000000:"
                    "11111111-1111-4111-8111-111111111111#/groups/value/0"
                ),
            },
        )
        self.assertEqual(self.document, original)

    def test_duplicate_groups_retain_first_source_reference(self):
        groups = self.document["groups"]
        groups["value"].append(deepcopy(groups["value"][0]))
        groups["@odata.count"] = 3
        records = normalize_azure(self.document)
        self.assertEqual(len(records), 2)
        self.assertTrue(records[0]["source_ref"].endswith("/value/0"))

    def test_next_page_and_inconsistent_total_are_not_treated_as_complete(self):
        for token in (
            "https://graph.microsoft.com/v1.0/users/example/memberOf?$skiptoken=next",
            42,
        ):
            with self.subTest(token=token):
                document = deepcopy(self.document)
                document["groups"]["@odata.nextLink"] = token
                with self.assertRaises(ValueError):
                    normalize_azure(document)
        self.document["groups"]["@odata.count"] = 3
        with self.assertRaisesRegex(ValueError, "complete value length"):
            normalize_azure(self.document)

    def test_non_group_or_untyped_object_fails_instead_of_disappearing(self):
        for object_type in (None, "#microsoft.graph.directoryRole", "#microsoft.graph.user"):
            with self.subTest(object_type=object_type):
                document = deepcopy(self.document)
                document["groups"]["value"][1]["@odata.type"] = object_type
                with self.assertRaises(ValueError):
                    normalize_azure(document)

    def test_nested_and_transitive_data_fail_closed(self):
        for extra in (
            {"members": []},
            {"memberOf": []},
            {"inheritedFrom": "parent"},
            {"members@odata.nextLink": "https://example.invalid/next"},
            {"@removed": {"reason": "deleted"}},
        ):
            with self.subTest(extra=extra):
                document = deepcopy(self.document)
                document["groups"]["value"][0].update(extra)
                with self.assertRaises(ValueError):
                    normalize_azure(document)
        self.document["groups"]["@odata.context"] = (
            "https://graph.microsoft.com/v1.0/$metadata#users('id')/transitiveMemberOf"
        )
        with self.assertRaisesRegex(ValueError, "transitive"):
            normalize_azure(self.document)

    def test_missing_identity_or_malformed_response_raises_value_error(self):
        for key, value in (
            ("principal_id", None),
            ("tenant_id", " "),
            ("groups", []),
            ("groups", {"value": {}}),
            ("groups", {"value": [None]}),
        ):
            with self.subTest(key=key, value=value):
                document = deepcopy(self.document)
                document[key] = value
                with self.assertRaises(ValueError):
                    normalize_azure(document)


class AwsAdapterTests(unittest.TestCase):
    def setUp(self):
        self.document = fixture("aws_direct_assignments.json")

    def test_direct_assignment_filters_other_users_without_mutating_input(self):
        original = deepcopy(self.document)
        records = normalize_aws(self.document)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["provider"], "aws")
        self.assertEqual(records[0]["principal_id"], self.document["principal_id"])
        self.assertEqual(records[0]["resource"], "123456789012")
        self.assertEqual(
            records[0]["entitlement_id"],
            "arn:aws:sso:::permissionSet/ssoins-0123456789abcdef/ps-0123456789abcdef",
        )
        self.assertTrue(records[0]["source_ref"].endswith("/AccountAssignments/0"))
        self.assertEqual(self.document, original)

    def test_account_mismatch_is_rejected_even_for_another_user(self):
        self.document["response"]["AccountAssignments"][1]["AccountId"] = "999999999999"
        with self.assertRaisesRegex(ValueError, "does not match"):
            normalize_aws(self.document)

    def test_groups_are_unresolved_even_when_group_id_differs_from_subject(self):
        self.document["response"]["AccountAssignments"][1]["PrincipalType"] = "GROUP"
        with self.assertRaisesRegex(ValueError, "unresolved GROUP"):
            normalize_aws(self.document)

    def test_duplicate_assignment_is_not_counted_twice(self):
        assignments = self.document["response"]["AccountAssignments"]
        assignments.append(deepcopy(assignments[0]))
        self.assertEqual(len(normalize_aws(self.document)), 1)

    def test_pagination_token_cannot_be_ignored(self):
        self.document["response"]["NextToken"] = "opaque-token"
        with self.assertRaisesRegex(ValueError, "incomplete pagination"):
            normalize_aws(self.document)
        for completed in (None, ""):
            with self.subTest(completed=completed):
                self.document["response"]["NextToken"] = completed
                self.assertEqual(len(normalize_aws(self.document)), 1)

    def test_mixed_permission_sets_are_not_misrepresented_as_one_api_response(self):
        self.document["response"]["AccountAssignments"][1]["PermissionSetArn"] = (
            "arn:aws:sso:::permissionSet/ssoins-0123456789abcdef/ps-fedcba9876543210"
        )
        with self.assertRaisesRegex(ValueError, "mixes permission sets"):
            normalize_aws(self.document)

    def test_invalid_account_and_permission_set_identifiers_are_rejected(self):
        for account in (123456789012, "12345", "１２３４５６７８９０１２", "123456789012 "):
            with self.subTest(account=account):
                document = deepcopy(self.document)
                document["account_id"] = account
                with self.assertRaises(ValueError):
                    normalize_aws(document)
        self.document["response"]["AccountAssignments"][0]["PermissionSetArn"] = (
            "arn:aws:iam::123456789012:role/Administrator"
        )
        with self.assertRaisesRegex(ValueError, "permission-set ARN"):
            normalize_aws(self.document)

    def test_error_metadata_and_missing_assignment_fields_fail_closed(self):
        self.document["response"]["ResponseMetadata"]["HTTPStatusCode"] = 403
        with self.assertRaisesRegex(ValueError, "non-success"):
            normalize_aws(self.document)
        self.document["response"]["ResponseMetadata"]["HTTPStatusCode"] = 200
        del self.document["response"]["AccountAssignments"][1]["PrincipalId"]
        with self.assertRaisesRegex(ValueError, "missing required"):
            normalize_aws(self.document)


class GcpAdapterTests(unittest.TestCase):
    def setUp(self):
        self.document = fixture("gcp_direct_policy.json")

    def test_workforce_principal_is_preserved_and_other_subject_is_ignored(self):
        original = deepcopy(self.document)
        records = normalize_gcp(self.document)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["entitlement_id"], "roles/viewer")
        self.assertTrue(
            all(record["principal_id"] == self.document["principal_id"] for record in records)
        )
        self.assertTrue(records[0]["source_ref"].endswith("/bindings/0/members/0"))
        self.assertEqual(self.document, original)

    def test_supported_individual_subject_forms_and_exact_matching(self):
        for principal in (
            "user:person@example.invalid",
            "serviceAccount:worker@synthetic-project.iam.gserviceaccount.com",
            "principal://iam.googleapis.com/projects/123456789012/locations/global/"
            "workloadIdentityPools/synthetic-pool/subject/workload-1",
        ):
            with self.subTest(principal=principal):
                document = deepcopy(self.document)
                document["principal_id"] = principal
                document["policy"]["bindings"] = [
                    {"role": "roles/viewer", "members": [principal, "user:other@example.invalid"]}
                ]
                self.assertEqual(len(normalize_gcp(document)), 1)
                document["principal_id"] += "-different"
                self.assertEqual(normalize_gcp(document), [])

    def test_duplicate_binding_and_member_preserve_first_evidence(self):
        binding = self.document["policy"]["bindings"][0]
        binding["members"].append(self.document["principal_id"])
        self.document["policy"]["bindings"].append(deepcopy(binding))
        records = normalize_gcp(self.document)
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]["source_ref"].endswith("/bindings/0/members/0"))

    def test_custom_project_role_is_preserved(self):
        self.document["policy"]["bindings"][0]["role"] = (
            "projects/synthetic-governance-demo/roles/financeReader"
        )
        records = normalize_gcp(self.document)
        self.assertEqual(
            records[0]["entitlement_id"], "projects/synthetic-governance-demo/roles/financeReader"
        )

    def test_conditions_fail_even_for_a_binding_to_another_user(self):
        for condition in (None, {}, {"expression": "true", "title": "always"}):
            with self.subTest(condition=condition):
                document = deepcopy(self.document)
                document["policy"]["bindings"].append(
                    {
                        "role": "roles/editor",
                        "members": ["user:other@example.invalid"],
                        "condition": condition,
                    }
                )
                with self.assertRaisesRegex(ValueError, "conditional"):
                    normalize_gcp(document)

    def test_legacy_condition_role_suffix_is_not_unconditional_access(self):
        self.document["policy"]["version"] = 1
        self.document["policy"]["bindings"][0]["role"] = "roles/viewer_withcond_a1b2c3"
        with self.assertRaisesRegex(ValueError, "requestedPolicyVersion=3"):
            normalize_gcp(self.document)

    def test_group_domain_public_wildcard_deleted_and_unknown_forms_fail(self):
        for member in (
            "group:staff@example.invalid",
            "domain:example.invalid",
            "allUsers",
            "allAuthenticatedUsers",
            "deleted:user:person@example.invalid?uid=123",
            "principalSet://iam.googleapis.com/locations/global/workforcePools/pool/group/team",
            "principalSet://iam.googleapis.com/locations/global/workforcePools/pool/*",
            "principal://iam.googleapis.com/locations/global/workforcePools/pool/subject/*",
            "principal://goog/subject/person@example.invalid",
            "not-a-principal",
            12,
        ):
            with self.subTest(member=member):
                document = deepcopy(self.document)
                document["policy"]["bindings"][0]["members"].append(member)
                with self.assertRaises(ValueError):
                    normalize_gcp(document)

    def test_inherited_and_incomplete_policy_envelopes_are_rejected(self):
        for field, value in (
            ("inheritedPolicies", []),
            ("nextPageToken", "next"),
            ("denyRules", []),
        ):
            with self.subTest(field=field):
                document = deepcopy(self.document)
                document["policy"][field] = value
                with self.assertRaisesRegex(ValueError, "unsupported fields"):
                    normalize_gcp(document)
        for field in ("version", "etag", "bindings"):
            with self.subTest(missing=field):
                document = deepcopy(self.document)
                del document["policy"][field]
                with self.assertRaisesRegex(ValueError, "missing required"):
                    normalize_gcp(document)

    def test_malformed_versions_etags_and_empty_members_are_rejected(self):
        for version in (0, 2, True, "3", None):
            with self.subTest(version=version):
                document = deepcopy(self.document)
                document["policy"]["version"] = version
                with self.assertRaises(ValueError):
                    normalize_gcp(document)
        for etag in ("", "not base64!", "AQ", 1):
            with self.subTest(etag=etag):
                document = deepcopy(self.document)
                document["policy"]["etag"] = etag
                with self.assertRaises(ValueError):
                    normalize_gcp(document)
        self.document["policy"]["bindings"][0]["members"] = []
        with self.assertRaisesRegex(ValueError, "at least one principal"):
            normalize_gcp(self.document)

    def test_supported_policy_versions_and_audit_logging_keep_direct_binding_result(self):
        expected = normalize_gcp(self.document)
        self.document["policy"]["auditConfigs"] = [
            {"service": "allServices", "auditLogConfigs": [{"logType": "DATA_READ"}]}
        ]
        for version in (1, 3):
            with self.subTest(version=version):
                self.document["policy"]["version"] = version
                self.assertEqual(normalize_gcp(self.document), expected)


class SharedAdapterContractTests(unittest.TestCase):
    def test_all_fixture_outputs_have_only_contract_fields_and_new_records(self):
        for normalize, name in (
            (normalize_azure, "azure_direct_groups.json"),
            (normalize_aws, "aws_direct_assignments.json"),
            (normalize_gcp, "gcp_direct_policy.json"),
        ):
            with self.subTest(name=name):
                document = fixture(name)
                first = normalize(document)
                second = normalize(document)
                for record in first:
                    self.assertEqual(set(record), OUTPUT_FIELDS)
                    self.assertTrue(
                        all(isinstance(value, str) and value for value in record.values())
                    )
                first[0]["principal_id"] = "changed-output-only"
                self.assertEqual(normalize(document), second)

    def test_empty_complete_snapshots_are_valid(self):
        azure = fixture("azure_direct_groups.json")
        azure["groups"] = {"value": []}
        aws = fixture("aws_direct_assignments.json")
        aws["response"] = {"AccountAssignments": []}
        gcp = fixture("gcp_direct_policy.json")
        gcp["policy"]["bindings"] = []
        for normalize, document in (
            (normalize_azure, azure),
            (normalize_aws, aws),
            (normalize_gcp, gcp),
        ):
            with self.subTest(normalize=normalize.__name__):
                self.assertEqual(normalize(document), [])

    def test_non_objects_and_unknown_scope_cannot_be_silently_accepted(self):
        for normalize, name in (
            (normalize_azure, "azure_direct_groups.json"),
            (normalize_aws, "aws_direct_assignments.json"),
            (normalize_gcp, "gcp_direct_policy.json"),
        ):
            with self.subTest(normalize=normalize.__name__):
                for malformed in (None, [], "{}", {1: "non-JSON-key"}):
                    with self.assertRaises(ValueError):
                        normalize(malformed)
                document = fixture(name)
                document["inherited"] = True
                with self.assertRaisesRegex(ValueError, "unsupported fields"):
                    normalize(document)


if __name__ == "__main__":
    unittest.main()
