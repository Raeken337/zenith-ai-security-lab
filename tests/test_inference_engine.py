import unittest

from models.model_config import (
    EXPECTED_CLASSES,
    SELECTED_FEATURES
)

from models.runtime.feature_engine import (
    FeatureEngine
)

from models.runtime.inference_engine import (
    ZenithInferenceEngine
)


class RuntimeInferenceTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.inference_engine = (
            ZenithInferenceEngine()
        )

    def setUp(self):
        self.feature_engine = (
            FeatureEngine()
        )

    def build_event(
        self,
        timestamp,
        event_type,
        resource=None
    ):
        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "username": "jake",
            "department": "finance",
            "role": "Financial Analyst",
            "source_device": "PC-FIN-01"
        }

        if resource is not None:
            event["resource"] = resource

        return event

    def test_saved_models_accept_runtime_features(
        self
    ):
        features = (
            self.feature_engine.process_event(
                self.build_event(
                    "2026-09-17T09:00:00",
                    "file_access_success",
                    resource="finance_reports"
                )
            )
        )

        assessment = (
            self.inference_engine.assess(
                features
            )
        )

        self.assertIn(
            assessment["classification"],
            EXPECTED_CLASSES
        )

        self.assertGreaterEqual(
            assessment["confidence"],
            0.0
        )

        self.assertLessEqual(
            assessment["confidence"],
            1.0
        )

        self.assertEqual(
            set(
                assessment[
                    "combined_probabilities"
                ]
            ),
            set(EXPECTED_CLASSES)
        )

        self.assertAlmostEqual(
            sum(
                assessment[
                    "combined_probabilities"
                ].values()
            ),
            1.0,
            places=7
        )

        self.assertEqual(
            set(
                assessment[
                    "feature_snapshot"
                ]
            ),
            set(SELECTED_FEATURES)
        )

    def test_assessment_contains_both_models(
        self
    ):
        features = (
            self.feature_engine.process_event(
                self.build_event(
                    "2026-09-17T09:00:00",
                    "login_success"
                )
            )
        )

        assessment = (
            self.inference_engine.assess(
                features
            )
        )

        self.assertEqual(
            assessment[
                "models"
            ][
                "random_forest"
            ][
                "role"
            ],
            "primary"
        )

        self.assertEqual(
            assessment[
                "models"
            ][
                "logistic_regression"
            ][
                "role"
            ],
            "supporting"
        )

        self.assertIn(
            assessment["agreement"],
            {
                "high",
                "moderate",
                "low"
            }
        )

        self.assertIsInstance(
            assessment[
                "security_disagreement"
            ],
            bool
        )

    def test_inference_rejects_missing_features(
        self
    ):
        features = (
            self.feature_engine.process_event(
                self.build_event(
                    "2026-09-17T09:00:00",
                    "login_success"
                )
            )
        )

        features.pop(
            "department"
        )

        with self.assertRaises(
            ValueError
        ):
            self.inference_engine.assess(
                features
            )


if __name__ == "__main__":
    unittest.main()