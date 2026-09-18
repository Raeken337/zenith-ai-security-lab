import io
import unittest

from contextlib import redirect_stdout

from hq.telemetry_viewer import (
    display_event,
    display_protocol_execution
)


class TelemetryViewerTests(
    unittest.TestCase
):
    def test_viewer_displays_model_reasoning(
        self
    ):
        event = {
            "timestamp":
                "2026-09-17T09:05:00",

            "zenith_received_at":
                "2026-09-17T09:05:01",

            "event_type":
                "file_access_denied",

            "origin_service":
                "file_server",

            "site":
                "HQ",

            "username":
                "jake",

            "department":
                "finance",

            "role":
                "Financial Analyst",

            "source_device":
                "PC-FIN-01",

            "resource":
                "remote_admin",

            "access_granted":
                False,

            "reason":
                "Role is not authorised",

            "zenith_features": {
                "failed_logins_10m": 2,
                "denied_accesses_10m": 3,
                "unique_resources_30m": 3,
                "recent_endpoints_used": 1,
                "resource_traversal_count": 3,
                "repeated_resource_accesses": 0,
                "off_hours": 0,
                "role_mismatch": 0,
                "device_mismatch": 0,
                "recent_password_reset": 0,
                "successful_recovery": 1,
                "department_resource_mismatch": 1,
                "resource_sensitivity": 4,
                "time_since_last_event_seconds": 60
            },

            "zenith_assessment": {
                "classification":
                    "suspicious",

                "confidence":
                    0.7343,

                "confidence_gap":
                    0.48,

                "agreement":
                    "high",

                "security_disagreement":
                    False,

                "combined_probabilities": {
                    "normal": 0.02,
                    "human_error": 0.20,
                    "suspicious": 0.7343,
                    "malicious": 0.0457
                },

                "models": {
                    "random_forest": {
                        "classification":
                            "suspicious",

                        "confidence":
                            0.72
                    },

                    "logistic_regression": {
                        "classification":
                            "suspicious",

                        "confidence":
                            0.8625
                    }
                }
            },

            "zenith_decision": {
                "classification":
                    "suspicious",

                "confidence":
                    0.7343,

                "event_importance": {
                    "level": 4,
                    "name": "critical"
                },

                "incident_severity": {
                    "level": 5,
                    "name": "critical"
                },

                "response_level":
                    4,

                "response_name":
                    "containment",

                "reasoning": [
                    (
                        "Three denied resource requests "
                        "show persistent probing."
                    ),

                    (
                        "Activity has traversed "
                        "3 resources."
                    ),

                    (
                        "The current resource has high "
                        "sensitivity (4/5)."
                    )
                ],

                "safeguards": [
                    (
                        "Suspicious activity may "
                        "recommend containment, but not "
                        "the highest critical response."
                    )
                ],

                "recommended_protocols": [
                    "record_event",
                    "increase_monitoring",
                    "open_incident",
                    "alert_administrator",
                    "require_step_up_authentication",
                    "invalidate_active_sessions",
                    "lock_account",
                    "isolate_endpoint"
                ],

                "privilege_context": {
                    "level": 0,
                    "name": "standard",
                    "role": "Financial Analyst"
                },

                "incident_state": {
                    "event_count": 6,
                    "security_assessment_count": 2,
                    "consecutive_security_assessments": 2,
                    "highest_severity_level": 5,
                    "highest_response_level": 4,
                    "last_classification": "suspicious",
                    "existing_actions": []
                }
            }
            
        }
        event["zenith_execution"] = {
            "executed_at":
                "2026-09-17T09:05:02",

            "classification":
                "suspicious",

            "response_level":
                4,

            "response_name":
                "containment",

            "applied_actions": [
                {
                    "action_id":
                        "lock-action-1",

                    "protocol":
                        "lock_account",

                    "target_type":
                        "user",

                    "target":
                        "jake",

                    "status":
                        "active",

                    "reason":
                        "Test containment",

                    "applied_at":
                        "2026-09-17T09:05:02",

                    "reversed_at":
                        None
                },

                {
                    "action_id":
                        "isolate-action-1",

                    "protocol":
                        "isolate_endpoint",

                    "target_type":
                        "endpoint",

                    "target":
                        "PC-FIN-01",

                    "status":
                        "active",

                    "reason":
                        "Test containment",

                    "applied_at":
                        "2026-09-17T09:05:02",

                    "reversed_at":
                        None
                }
            ],

            "already_active": [
                {
                    "action_id":
                        "monitor-action-1",

                    "protocol":
                        "increase_monitoring",

                    "target_type":
                        "user",

                    "target":
                        "jake",

                    "status":
                        "active",

                    "reason":
                        "Earlier alert",

                    "applied_at":
                        "2026-09-17T09:04:00",

                    "reversed_at":
                        None
                }
            ],

            "satisfied_protocols": [
                "record_event"
            ],

            "skipped_protocols":
                [],

            "active_protocols": [
                "alert_administrator",
                "increase_monitoring",
                "invalidate_active_sessions",
                "isolate_endpoint",
                "lock_account",
                "open_incident",
                "require_step_up_authentication"
            ]
        }
        output = io.StringIO()

        with redirect_stdout(
            output
        ):
            display_event(
                event,
                number=1
            )

        rendered_output = (
            output.getvalue()
        )

        self.assertIn(
            "Zenith Analysis",
            rendered_output
        )

        self.assertIn(
            "Combined assessment: "
            "Suspicious (73.43%)",
            rendered_output
        )

        self.assertIn(
            "3 denied resource request(s)",
            rendered_output
        )

        self.assertIn(
            "movement across 3 resources",
            rendered_output
        )

        self.assertIn(
            "current resource sensitivity "
            "is 4/5",
            rendered_output
        )
        self.assertIn(
            "Zenith Decision",
            rendered_output
        )

        self.assertIn(
            "Response: Level 4 - Containment",
            rendered_output
        )

        self.assertIn(
            "Why Zenith selected this response:",
            rendered_output
        )

        self.assertIn(
            "Lock Account",
            rendered_output
        )

        self.assertIn(
            "Isolate Endpoint",
            rendered_output
        )

        self.assertIn(
            "Highest response level: 4",
            rendered_output
        )
        self.assertIn(
            "Zenith Protocol Execution",
            rendered_output
        )

        self.assertIn(
            "Execution status: Completed",
            rendered_output
        )

        self.assertIn(
            "Lock Account -> User: jake",
            rendered_output
        )

        self.assertIn(
            (
                "Isolate Endpoint -> "
                "Endpoint: PC-FIN-01"
            ),
            rendered_output
        )

        self.assertIn(
            (
                "Increase Monitoring -> "
                "User: jake"
            ),
            rendered_output
        )

        self.assertIn(
            "Record Event",
            rendered_output
        )        

    def test_viewer_handles_legacy_event(
        self
    ):
        event = {
            "timestamp":
                "2026-09-17T09:00:00",

            "event_type":
                "login_success",

            "username":
                "jake",

            "source_device":
                "PC-FIN-01"
        }

        output = io.StringIO()

        with redirect_stdout(
            output
        ):
            display_event(
                event
            )

        self.assertIn(
            "No model analysis is stored "
            "for this event.",
            output.getvalue()
        )

    def test_viewer_displays_protocol_execution_error(
        self
    ):
        output = io.StringIO()

        with redirect_stdout(
            output
        ):
            display_protocol_execution(
                execution=None,
                execution_error=(
                    "OSError: State unavailable"
                )
            )

        rendered_output = (
            output.getvalue()
        )

        self.assertIn(
            "Execution status: Failed",
            rendered_output
        )

        self.assertIn(
            "OSError: State unavailable",
            rendered_output
        )
        
if __name__ == "__main__":
    unittest.main()