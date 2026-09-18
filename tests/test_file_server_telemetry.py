import unittest
import tempfile
from unittest.mock import patch

from hq.file_server import (
    handle_file_request
)
from pathlib import Path

from simulation.defensive_state import (
    DefensiveStateStore
)

class FileServerTelemetryTests(
    unittest.TestCase
):

    def setUp(self):
        self.temporary_directory = (
            tempfile.TemporaryDirectory()
        )

        state_file = (
            Path(
                self.temporary_directory.name
            )
            / "defensive_state.json"
        )

        self.state_store = (
            DefensiveStateStore(
                state_file=state_file
            )
        )

        self.state_patch = patch(
            "hq.file_server."
            "DEFENSIVE_STATE",
            self.state_store
        )

        self.state_patch.start()

    def tearDown(self):
        self.state_patch.stop()
        self.temporary_directory.cleanup()

    def build_valid_session(self):
        return {
            "valid": True,
            "reason": "Session validated",
            "username": "jake",
            "full_name": "Jake Morgan",
            "department": "finance",
            "groups": [
                "employees",
                "finance"
            ],
            "role": "Financial Analyst",
            "work_start": 8,
            "work_end": 17,
            "source_device": "PC-FIN-01"
        }

    @patch(
        "hq.file_server."
        "log_file_access_event"
    )
    def test_missing_session_is_logged(
        self,
        mock_log_event
    ):
        response = handle_file_request({
            "source_device": "UNKNOWN-PC",
            "resource": "finance_reports"
        })

        self.assertFalse(
            response["access_granted"]
        )

        self.assertEqual(
            response["reason"],
            "Session token missing"
        )

        mock_log_event.assert_called_once_with(
            username="unknown",
            source_device="UNKNOWN-PC",
            resource="finance_reports",
            access_granted=False,
            reason="Session token missing",
            department="unknown",
            role="unknown"
        )

    @patch(
        "hq.file_server."
        "log_file_access_event"
    )
    @patch(
        "hq.file_server."
        "validate_session_with_identity_server"
    )
    def test_invalid_session_is_logged(
        self,
        mock_validate_session,
        mock_log_event
    ):
        mock_validate_session.return_value = {
            "valid": False,
            "reason": "Invalid session token"
        }

        response = handle_file_request({
            "session_token": "invalid-token",
            "source_device": "UNKNOWN-PC",
            "resource": "finance_reports"
        })

        self.assertFalse(
            response["access_granted"]
        )

        self.assertEqual(
            response["reason"],
            "Invalid session token"
        )

        mock_log_event.assert_called_once_with(
            username="unknown",
            source_device="UNKNOWN-PC",
            resource="finance_reports",
            access_granted=False,
            reason="Invalid session token",
            department="unknown",
            role="unknown"
        )

    @patch(
        "hq.file_server."
        "log_file_access_event"
    )
    @patch(
        "hq.file_server."
        "validate_session_with_identity_server"
    )
    def test_missing_resource_is_logged(
        self,
        mock_validate_session,
        mock_log_event
    ):
        mock_validate_session.return_value = (
            self.build_valid_session()
        )

        response = handle_file_request({
            "session_token": "valid-token",
            "source_device": "PC-FIN-01"
        })

        self.assertFalse(
            response["access_granted"]
        )

        self.assertEqual(
            response["reason"],
            "Resource not specified"
        )

        mock_log_event.assert_called_once_with(
            username="jake",
            source_device="PC-FIN-01",
            resource=None,
            access_granted=False,
            reason="Resource not specified",
            department="finance",
            role="Financial Analyst"
        )

    @patch(
        "hq.file_server."
        "log_file_access_event"
    )
    @patch(
        "hq.file_server."
        "validate_session_with_identity_server"
    )
    def test_session_device_mismatch_is_logged(
        self,
        mock_validate_session,
        mock_log_event
    ):
        mock_validate_session.return_value = (
            self.build_valid_session()
        )

        response = handle_file_request({
            "session_token": "valid-token",
            "source_device": "PC-HR-01",
            "resource": "finance_reports"
        })

        self.assertFalse(
            response["access_granted"]
        )

        self.assertEqual(
            response["reason"],
            (
                "Session is not valid "
                "for this device"
            )
        )

        mock_log_event.assert_called_once_with(
            username="jake",
            source_device="PC-HR-01",
            resource="finance_reports",
            access_granted=False,
            reason=(
                "Session is not valid "
                "for this device"
            ),
            department="finance",
            role="Financial Analyst"
        )

    @patch(
        "hq.file_server."
        "log_file_access_event"
    )
    @patch(
        "hq.file_server."
        "validate_session_with_identity_server"
    )
    def test_known_invalid_session_preserves_identity_context(
        self,
        mock_validate_session,
        mock_log_event
    ):
        mock_validate_session.return_value = {
            "valid": False,
            "reason": (
                "Session invalidated by Zenith"
            ),
            "username": "jake",
            "department": "finance",
            "role": "Financial Analyst"
        }

        response = handle_file_request({
            "session_token": "known-token",
            "source_device": "PC-FIN-01",
            "resource": "finance_reports"
        })

        self.assertFalse(
            response["access_granted"]
        )

        self.assertEqual(
            response["reason"],
            "Session invalidated by Zenith"
        )

        mock_log_event.assert_called_once_with(
            username="jake",
            source_device="PC-FIN-01",
            resource="finance_reports",
            access_granted=False,
            reason=(
                "Session invalidated by Zenith"
            ),
            department="finance",
            role="Financial Analyst"
        )

    @patch(
        "hq.file_server."
        "log_file_access_event"
    )
    @patch(
        "hq.file_server."
        "validate_session_with_identity_server"
    )
    def test_isolated_endpoint_is_blocked(
        self,
        mock_validate_session,
        mock_log_event
    ):
        mock_validate_session.return_value = (
            self.build_valid_session()
        )

        self.state_store.apply_action(
            protocol="isolate_endpoint",
            target_type="endpoint",
            target="PC-FIN-01",
            reason="Test containment"
        )

        response = handle_file_request({
            "session_token": "valid-token",
            "source_device": "PC-FIN-01",
            "resource": "finance_reports"
        })

        self.assertFalse(
            response["access_granted"]
        )

        self.assertEqual(
            response["reason"],
            "Endpoint isolated by Zenith"
        )

        mock_log_event.assert_called_once_with(
            username="jake",
            source_device="PC-FIN-01",
            resource="finance_reports",
            access_granted=False,
            reason="Endpoint isolated by Zenith",
            department="finance",
            role="Financial Analyst"
        )

    @patch(
        "hq.file_server."
        "log_file_access_event"
    )
    @patch(
        "hq.file_server."
        "validate_session_with_identity_server"
    )
    def test_lateral_movement_restriction_is_enforced(
        self,
        mock_validate_session,
        mock_log_event
    ):
        mock_validate_session.return_value = (
            self.build_valid_session()
        )

        self.state_store.apply_action(
            protocol=(
                "restrict_lateral_movement"
            ),
            target_type="endpoint",
            target="PC-FIN-01",
            reason="Test containment"
        )

        response = handle_file_request({
            "session_token": "valid-token",
            "source_device": "PC-FIN-01",
            "resource": "finance_reports"
        })

        self.assertFalse(
            response["access_granted"]
        )

        self.assertEqual(
            response["reason"],
            (
                "Lateral movement restricted "
                "by Zenith"
            )
        )

        mock_log_event.assert_called_once_with(
            username="jake",
            source_device="PC-FIN-01",
            resource="finance_reports",
            access_granted=False,
            reason=(
                "Lateral movement restricted "
                "by Zenith"
            ),
            department="finance",
            role="Financial Analyst"
        )

    @patch(
        "hq.file_server."
        "log_file_access_event"
    )
    @patch(
        "hq.file_server."
        "validate_session_with_identity_server"
    )
    def test_protected_resource_is_blocked(
        self,
        mock_validate_session,
        mock_log_event
    ):
        mock_validate_session.return_value = (
            self.build_valid_session()
        )

        self.state_store.apply_action(
            protocol="protect_target_resource",
            target_type="resource",
            target="finance_reports",
            reason="Test containment"
        )

        response = handle_file_request({
            "session_token": "valid-token",
            "source_device": "PC-FIN-01",
            "resource": "finance_reports"
        })

        self.assertFalse(
            response["access_granted"]
        )

        self.assertEqual(
            response["reason"],
            "Resource protected by Zenith"
        )

        mock_log_event.assert_called_once_with(
            username="jake",
            source_device="PC-FIN-01",
            resource="finance_reports",
            access_granted=False,
            reason="Resource protected by Zenith",
            department="finance",
            role="Financial Analyst"
        )
        
if __name__ == "__main__":
    unittest.main()