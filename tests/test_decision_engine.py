import unittest

from models.runtime.decision_engine import (
    ZenithDecisionEngine
)


class ZenithDecisionEngineTests(
    unittest.TestCase
):
    def setUp(self):
        self.engine = (
            ZenithDecisionEngine()
        )

    def build_event(
        self,
        event_type="login_success",
        resource=None
    ):
        event = {
            "username": "jake",
            "event_type": event_type
        }

        if resource is not None:
            event["resource"] = resource

        return event

    def build_features(
        self,
        **changes
    ):
        features = {
            "department": "finance",
            "role": "Financial Analyst",
            "event_type": "login_success",
            "hour": 10,
            "failed_logins_10m": 0,
            "denied_accesses_10m": 0,
            "unique_resources_30m": 0,
            "off_hours": 0,
            "role_mismatch": 0,
            "device_mismatch": 0,
            "recent_password_reset": 0,
            "successful_recovery": 0,
            "department_resource_mismatch": 0,
            "resource_sensitivity": 0,
            "recent_endpoints_used": 1,
            "time_since_last_event_seconds": 30,
            "repeated_resource_accesses": 0,
            "resource_traversal_count": 0
        }

        features.update(
            changes
        )

        return features

    def build_assessment(
        self,
        classification,
        confidence,
        agreement="high",
        security_disagreement=False,
        random_forest_class=None,
        logistic_regression_class=None
    ):
        random_forest_class = (
            random_forest_class
            or classification
        )

        logistic_regression_class = (
            logistic_regression_class
            or classification
        )

        return {
            "classification":
                classification,

            "confidence":
                confidence,

            "agreement":
                agreement,

            "security_disagreement":
                security_disagreement,

            "models": {
                "random_forest": {
                    "classification":
                        random_forest_class,

                    "confidence":
                        confidence
                },

                "logistic_regression": {
                    "classification":
                        logistic_regression_class,

                    "confidence":
                        confidence
                }
            }
        }

    def test_normal_activity_is_recorded_only(
        self
    ):
        decision = self.engine.decide(
            event=self.build_event(),
            features=self.build_features(),
            assessment=self.build_assessment(
                classification="normal",
                confidence=1.0
            )
        )

        self.assertEqual(
            decision["response_level"],
            0
        )

        self.assertEqual(
            decision[
                "recommended_protocols"
            ],
            ["record_event"]
        )

    def test_recovery_without_probing_is_observed(
        self
    ):
        decision = self.engine.decide(
            event=self.build_event(),
            features=self.build_features(
                failed_logins_10m=2,
                recent_password_reset=1,
                successful_recovery=1
            ),
            assessment=self.build_assessment(
                classification="human_error",
                confidence=0.84
            )
        )

        self.assertLessEqual(
            decision["response_level"],
            1
        )

        self.assertNotIn(
            "lock_account",
            decision[
                "recommended_protocols"
            ]
        )

        self.assertNotIn(
            "isolate_endpoint",
            decision[
                "recommended_protocols"
            ]
        )

    def test_low_agreement_prevents_containment(
        self
    ):
        decision = self.engine.decide(
            event=self.build_event(
                event_type=(
                    "file_access_denied"
                ),
                resource="employee_records"
            ),
            features=self.build_features(
                event_type=(
                    "file_access_denied"
                ),
                failed_logins_10m=2,
                denied_accesses_10m=2,
                unique_resources_30m=2,
                department_resource_mismatch=1,
                resource_sensitivity=3,
                resource_traversal_count=2
            ),
            assessment=self.build_assessment(
                classification="suspicious",
                confidence=0.4974,
                agreement="low",
                security_disagreement=True,
                random_forest_class=(
                    "suspicious"
                ),
                logistic_regression_class=(
                    "human_error"
                )
            )
        )

        self.assertEqual(
            decision["response_level"],
            2
        )

        self.assertIn(
            "alert_administrator",
            decision[
                "recommended_protocols"
            ]
        )

        self.assertNotIn(
            "isolate_endpoint",
            decision[
                "recommended_protocols"
            ]
        )

    def test_persistent_high_sensitivity_probing_recommends_containment(
        self
    ):
        self.engine.decide(
            event=self.build_event(
                event_type=(
                    "file_access_denied"
                ),
                resource="employee_records"
            ),
            features=self.build_features(
                event_type=(
                    "file_access_denied"
                ),
                failed_logins_10m=2,
                denied_accesses_10m=2,
                unique_resources_30m=2,
                department_resource_mismatch=1,
                resource_sensitivity=3,
                resource_traversal_count=2
            ),
            assessment=self.build_assessment(
                classification="suspicious",
                confidence=0.4974,
                agreement="low",
                security_disagreement=True,
                random_forest_class=(
                    "suspicious"
                ),
                logistic_regression_class=(
                    "human_error"
                )
            )
        )

        decision = self.engine.decide(
            event=self.build_event(
                event_type=(
                    "file_access_denied"
                ),
                resource="remote_admin"
            ),
            features=self.build_features(
                event_type=(
                    "file_access_denied"
                ),
                failed_logins_10m=2,
                denied_accesses_10m=3,
                unique_resources_30m=3,
                department_resource_mismatch=1,
                resource_sensitivity=4,
                resource_traversal_count=3
            ),
            assessment=self.build_assessment(
                classification="suspicious",
                confidence=0.7343,
                agreement="high"
            )
        )

        self.assertEqual(
            decision["response_level"],
            4
        )

        self.assertEqual(
            decision[
                "response_name"
            ],
            "containment"
        )

        self.assertIn(
            "lock_account",
            decision[
                "recommended_protocols"
            ]
        )

        self.assertIn(
            "isolate_endpoint",
            decision[
                "recommended_protocols"
            ]
        )

    def test_existing_action_is_not_recommended_again(
        self
    ):
        decision = self.engine.decide(
            event=self.build_event(
                event_type=(
                    "file_access_denied"
                ),
                resource="employee_records"
            ),
            features=self.build_features(
                event_type=(
                    "file_access_denied"
                ),
                denied_accesses_10m=2,
                department_resource_mismatch=1,
                resource_sensitivity=3,
                resource_traversal_count=2
            ),
            assessment=self.build_assessment(
                classification="suspicious",
                confidence=0.65
            ),
            existing_actions=[
                "alert_administrator"
            ]
        )

        self.assertNotIn(
            "alert_administrator",
            decision[
                "recommended_protocols"
            ]
        )

        self.assertIn(
            "alert_administrator",
            decision[
                "incident_state"
            ][
                "existing_actions"
            ]
        )

    def test_reversed_action_can_be_recommended_again(
        self
    ):
        event = self.build_event(
            event_type=(
                "file_access_denied"
            ),
            resource="remote_admin"
        )

        features = self.build_features(
            event_type=(
                "file_access_denied"
            ),
            failed_logins_10m=2,
            denied_accesses_10m=3,
            unique_resources_30m=3,
            department_resource_mismatch=1,
            resource_sensitivity=4,
            resource_traversal_count=3
        )

        assessment = (
            self.build_assessment(
                classification="suspicious",
                confidence=0.75,
                agreement="high"
            )
        )

        action_still_active = (
            self.engine.decide(
                event=event,
                features=features,
                assessment=assessment,
                existing_actions=[
                    "lock_account",
                    "isolate_endpoint"
                ]
            )
        )

        self.assertNotIn(
            "lock_account",
            action_still_active[
                "recommended_protocols"
            ]
        )

        self.assertNotIn(
            "isolate_endpoint",
            action_still_active[
                "recommended_protocols"
            ]
        )

        action_was_reversed = (
            self.engine.decide(
                event=event,
                features=features,
                assessment=assessment,
                existing_actions=[]
            )
        )

        self.assertIn(
            "lock_account",
            action_was_reversed[
                "recommended_protocols"
            ]
        )

        self.assertIn(
            "isolate_endpoint",
            action_was_reversed[
                "recommended_protocols"
            ]
        )
        
if __name__ == "__main__":
    unittest.main()