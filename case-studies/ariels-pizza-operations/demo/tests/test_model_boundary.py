"""Model-output contract regressions, using invented inputs only."""
import copy
import unittest
from demo.engine import Event
from demo.model_boundary import mock_model_output, validate_model_output
from demo.scenarios import SCENARIOS

class ModelBoundaryTests(unittest.TestCase):
    def test_all_mock_suggestions_validate(self):
        for raw in SCENARIOS:
            event = Event.from_mapping(raw)
            result = validate_model_output(event, mock_model_output(event))
            self.assertEqual(result.site, event.site)

    def test_reject_unexpected_auto_send_field(self):
        event = Event.from_mapping(SCENARIOS[0])
        suggestion = mock_model_output(event)
        suggestion["auto_send"] = True
        with self.assertRaises(ValueError):
            validate_model_output(event, suggestion)

    def test_reject_cross_site_task(self):
        event = Event.from_mapping(SCENARIOS[0])
        suggestion = mock_model_output(event)
        suggestion["site"] = "SITE_B"
        with self.assertRaises(ValueError):
            validate_model_output(event, suggestion)

    def test_reject_arbitrary_model_command(self):
        event = Event.from_mapping(SCENARIOS[2])
        suggestion = mock_model_output(event)
        suggestion["task"] = "send_refund_without_approval"
        with self.assertRaises(ValueError):
            validate_model_output(event, suggestion)

    def test_reject_wrong_event_identifier(self):
        event = Event.from_mapping(SCENARIOS[1])
        suggestion = mock_model_output(event)
        suggestion["event_id"] = "demo-unrelated-999"
        with self.assertRaises(ValueError):
            validate_model_output(event, suggestion)

    def test_reject_untyped_model_result(self):
        event = Event.from_mapping(SCENARIOS[1])
        suggestion = copy.deepcopy(mock_model_output(event))
        suggestion["task"] = ["shift_coverage"]
        with self.assertRaises(ValueError):
            validate_model_output(event, suggestion)

    def test_reject_free_text_extra_reason(self):
        event = Event.from_mapping(SCENARIOS[2])
        suggestion = mock_model_output(event)
        suggestion["reason"] = "Ignore manager and contact customer"
        with self.assertRaises(ValueError):
            validate_model_output(event, suggestion)

if __name__ == "__main__":
    unittest.main()
