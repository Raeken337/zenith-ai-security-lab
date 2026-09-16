import unittest

from models.runtime.feature_engine import (
    FeatureEngine
)


class HumanFactorFeatureTests(
    unittest.TestCase
):
    def setUp(self):
        self.feature_engine = FeatureEngine()

    def process_events(self, events):
        features = None

        for event in events:
            features = (
                self.feature_engine.process_event(
                    event
                )
            )

        return features

    def build_event(
        self,
        timestamp,
        event_type,
        resource=None,
        source_device="PC-FIN-01"
    ):
        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "username": "jake",
            "department": "finance",
            "role": "Financial Analyst",
            "source_device": source_device
        }

        if resource is not None:
            event["resource"] = resource

        return event

    def test_password_reset_recovery_followed_by_legitimate_access(
        self
    ):
        events = [
            self.build_event(
                "2026-09-16T08:55:00",
                "login_failure"
            ),

            self.build_event(
                "2026-09-16T08:56:00",
                "login_failure"
            ),

            self.build_event(
                "2026-09-16T08:57:00",
                "password_reset"
            ),

            self.build_event(
                "2026-09-16T08:58:00",
                "login_success"
            ),

            self.build_event(
                "2026-09-16T09:00:00",
                "file_access_success",
                resource="finance_reports"
            )
        ]

        features = self.process_events(
            events
        )

        self.assertEqual(
            features["failed_logins_10m"],
            2
        )

        self.assertEqual(
            features["recent_password_reset"],
            1
        )

        self.assertEqual(
            features["successful_recovery"],
            1
        )

        self.assertEqual(
            features["denied_accesses_10m"],
            0
        )

        self.assertEqual(
            features[
                "department_resource_mismatch"
            ],
            0
        )

        self.assertEqual(
            features["device_mismatch"],
            0
        )

        self.assertEqual(
            features["unique_resources_30m"],
            1
        )

        self.assertEqual(
            features[
                "resource_traversal_count"
            ],
            1
        )

        self.assertEqual(
            features[
                "time_since_last_event_seconds"
            ],
            120
        )

    def test_login_recovery_followed_by_unauthorised_access(
        self
    ):
        events = [
            self.build_event(
                "2026-09-16T09:00:00",
                "login_failure"
            ),

            self.build_event(
                "2026-09-16T09:01:00",
                "login_failure"
            ),

            self.build_event(
                "2026-09-16T09:02:00",
                "login_success"
            ),

            self.build_event(
                "2026-09-16T09:03:00",
                "file_access_denied",
                resource="hr_records"
            )
        ]

        features = self.process_events(
            events
        )

        self.assertEqual(
            features["failed_logins_10m"],
            2
        )

        self.assertEqual(
            features["recent_password_reset"],
            0
        )

        self.assertEqual(
            features["successful_recovery"],
            1
        )

        self.assertEqual(
            features["denied_accesses_10m"],
            1
        )

        self.assertEqual(
            features[
                "department_resource_mismatch"
            ],
            1
        )

        self.assertEqual(
            features["resource_sensitivity"],
            3
        )

        self.assertEqual(
            features["unique_resources_30m"],
            1
        )

        self.assertEqual(
            features[
                "resource_traversal_count"
            ],
            1
        )

    def test_single_access_mistake_followed_by_normal_work(
        self
    ):
        events = [
            self.build_event(
                "2026-09-16T09:00:00",
                "login_success"
            ),

            self.build_event(
                "2026-09-16T09:02:00",
                "file_access_denied",
                resource="hr_records"
            ),

            self.build_event(
                "2026-09-16T09:04:00",
                "file_access_success",
                resource="finance_reports"
            )
        ]

        features = self.process_events(
            events
        )

        self.assertEqual(
            features["denied_accesses_10m"],
            1
        )

        self.assertEqual(
            features["unique_resources_30m"],
            2
        )

        self.assertEqual(
            features[
                "resource_traversal_count"
            ],
            2
        )

        self.assertEqual(
            features[
                "department_resource_mismatch"
            ],
            0
        )

        self.assertEqual(
            features["device_mismatch"],
            0
        )

    def test_repeated_cross_department_probing_accumulates_evidence(
        self
    ):
        events = [
            self.build_event(
                "2026-09-16T09:00:00",
                "login_failure"
            ),

            self.build_event(
                "2026-09-16T09:01:00",
                "login_failure"
            ),

            self.build_event(
                "2026-09-16T09:02:00",
                "login_success"
            ),

            self.build_event(
                "2026-09-16T09:03:00",
                "file_access_denied",
                resource="hr_records"
            ),

            self.build_event(
                "2026-09-16T09:04:00",
                "file_access_denied",
                resource="employee_records"
            ),

            self.build_event(
                "2026-09-16T09:05:00",
                "file_access_denied",
                resource="remote_admin"
            )
        ]

        features = self.process_events(
            events
        )

        self.assertEqual(
            features["failed_logins_10m"],
            2
        )

        self.assertEqual(
            features["successful_recovery"],
            1
        )

        self.assertEqual(
            features["denied_accesses_10m"],
            3
        )

        self.assertEqual(
            features["unique_resources_30m"],
            3
        )

        self.assertEqual(
            features[
                "resource_traversal_count"
            ],
            3
        )

        self.assertEqual(
            features[
                "department_resource_mismatch"
            ],
            1
        )

        self.assertEqual(
            features["resource_sensitivity"],
            4
        )

    def test_endpoint_switch_adds_device_evidence(
        self
    ):
        events = [
            self.build_event(
                "2026-09-16T09:00:00",
                "login_success"
            ),

            self.build_event(
                "2026-09-16T09:01:00",
                "file_access_success",
                resource="finance_reports",
                source_device="PC-HR-01"
            )
        ]

        features = self.process_events(
            events
        )

        self.assertEqual(
            features["device_mismatch"],
            1
        )

        self.assertEqual(
            features["recent_endpoints_used"],
            2
        )

        self.assertEqual(
            features["resource_sensitivity"],
            2
        )

    def test_recovery_evidence_expires_after_window(
        self
    ):
        events = [
            self.build_event(
                "2026-09-16T09:00:00",
                "login_failure"
            ),

            self.build_event(
                "2026-09-16T09:01:00",
                "login_failure"
            ),

            self.build_event(
                "2026-09-16T09:02:00",
                "password_reset"
            ),

            self.build_event(
                "2026-09-16T09:03:00",
                "login_success"
            ),

            self.build_event(
                "2026-09-16T09:14:00",
                "file_access_success",
                resource="finance_reports"
            )
        ]

        features = self.process_events(
            events
        )

        self.assertEqual(
            features["failed_logins_10m"],
            0
        )

        self.assertEqual(
            features["recent_password_reset"],
            0
        )

        self.assertEqual(
            features["successful_recovery"],
            0
        )

        self.assertEqual(
            features[
                "time_since_last_event_seconds"
            ],
            660
        )
        
if __name__ == "__main__":
    unittest.main()