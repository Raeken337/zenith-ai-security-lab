import unittest

from unittest.mock import patch

from hq.file_server import (
    handle_file_request
)


class FileServerTelemetryTests(
    unittest.TestCase
):
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


if __name__ == "__main__":
    unittest.main()