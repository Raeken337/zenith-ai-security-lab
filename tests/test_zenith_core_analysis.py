import json
import tempfile
import unittest

from pathlib import Path
from unittest.mock import (
    Mock,
    patch
)

from hq.zenith_core import (
    analyse_event,
    process_event,
    store_event
)

from models.runtime.feature_engine import (
    FeatureEngine
)

from models.runtime.inference_engine import (
    ZenithInferenceEngine
)

from models.runtime.decision_engine import (
    ZenithDecisionEngine
)
from simulation.defensive_state import (
    DefensiveStateStore
)

from simulation.protocol_executor import (
    ZenithProtocolExecutor
)


class ZenithCoreAnalysisTests(
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

        self.decision_engine = (
            ZenithDecisionEngine()
        )
        self.state_directory = (
            tempfile.TemporaryDirectory()
        )

        state_file = (
            Path(
                self.state_directory.name
            )
            / "defensive_state.json"
        )

        self.state_store = (
            DefensiveStateStore(
                state_file=state_file
            )
        )

        self.protocol_executor = (
            ZenithProtocolExecutor(
                state_store=self.state_store
            )
        )

    def tearDown(self):
        self.state_directory.cleanup()

    def build_event(self):
        return {
            "timestamp":
                "2026-09-17T09:00:00",

            "event_type":
                "login_success",

            "origin_service":
                "identity_server",

            "site":
                "HQ",

            "username":
                "jake",

            "source_device":
                "PC-FIN-01",

            "department":
                "finance",

            "groups": [
                "employees",
                "finance"
            ],

            "role":
                "Financial Analyst",

            "authenticated":
                True,

            "reason":
                "Login successful"
        }

    def test_event_produces_features_and_assessment(
        self
    ):
        (
            features,
            assessment
        ) = analyse_event(
            self.build_event(),
            self.feature_engine,
            self.inference_engine
        )

        self.assertEqual(
            features["failed_logins_10m"],
            0
        )

        self.assertEqual(
            features["device_mismatch"],
            0
        )

        self.assertEqual(
            assessment["classification"],
            "normal"
        )

        self.assertIn(
            "random_forest",
            assessment["models"]
        )

        self.assertIn(
            "logistic_regression",
            assessment["models"]
        )

    def test_central_event_contains_analysis(
        self
    ):
        event = self.build_event()

        (
            features,
            assessment
        ) = analyse_event(
            event,
            self.feature_engine,
            self.inference_engine
        )

        with tempfile.TemporaryDirectory() as (
            temporary_directory
        ):
            temporary_log = (
                Path(temporary_directory)
                / "central_telemetry.jsonl"
            )

            with patch(
                "hq.zenith_core."
                "CENTRAL_LOG_FILE",
                temporary_log
            ):
                central_event = store_event(
                    event,
                    features=features,
                    assessment=assessment
                )

            stored_lines = (
                temporary_log.read_text(
                    encoding="utf-8"
                ).splitlines()
            )

            self.assertEqual(
                len(stored_lines),
                1
            )

            stored_event = json.loads(
                stored_lines[0]
            )

            self.assertIn(
                "zenith_features",
                stored_event
            )

            self.assertIn(
                "zenith_assessment",
                stored_event
            )

            self.assertEqual(
                stored_event[
                    "zenith_assessment"
                ][
                    "classification"
                ],
                "normal"
            )

            self.assertEqual(
                central_event,
                stored_event
            )

    def test_analysis_failure_still_stores_event(
        self
    ):
        invalid_event = self.build_event()

        invalid_event.pop(
            "username"
        )

        with tempfile.TemporaryDirectory() as (
            temporary_directory
        ):
            temporary_log = (
                Path(temporary_directory)
                / "central_telemetry.jsonl"
            )

            with patch(
                "hq.zenith_core."
                "CENTRAL_LOG_FILE",
                temporary_log
            ):
                (
                    central_event,
                    response
                ) = process_event(
                    invalid_event,
                    self.feature_engine,
                    self.inference_engine,
                    self.decision_engine,
                    self.protocol_executor
                )

            self.assertTrue(
                response["received"]
            )

            self.assertFalse(
                response["analysed"]
            )

            self.assertIn(
                "zenith_analysis_error",
                central_event
            )

            self.assertTrue(
                temporary_log.exists()
            )

    def test_central_event_contains_decision(
        self
    ):
        event = self.build_event()

        with tempfile.TemporaryDirectory() as (
            temporary_directory
        ):
            temporary_log = (
                Path(temporary_directory)
                / "central_telemetry.jsonl"
            )

            with patch(
                "hq.zenith_core."
                "CENTRAL_LOG_FILE",
                temporary_log
            ):
                (
                    central_event,
                    response
                ) = process_event(
                    event,
                    self.feature_engine,
                    self.inference_engine,
                    self.decision_engine,
                    self.protocol_executor
                )

        self.assertTrue(
            response["decision_created"]
        )

        self.assertIn(
            "zenith_decision",
            central_event
        )
        self.assertIn(
            "zenith_execution",
            central_event
        )

        self.assertTrue(
            response[
                "protocols_executed"
            ]
        )

        self.assertEqual(
            central_event[
                "zenith_execution"
            ][
                "satisfied_protocols"
            ],
            ["record_event"]
        )

        decision = central_event[
            "zenith_decision"
        ]

        self.assertEqual(
            decision["classification"],
            "normal"
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

    def test_recommended_protocols_create_shared_state(
        self
    ):
        event = self.build_event()

        simulated_decision_engine = (
            Mock()
        )

        simulated_decision_engine.decide.return_value = {
            "classification":
                "suspicious",

            "confidence":
                0.70,

            "event_importance": {
                "level": 3,
                "name": "high"
            },

            "incident_severity": {
                "level": 4,
                "name": "high"
            },

            "response_level":
                2,

            "response_name":
                "alert_and_review",

            "reasoning": [
                "Repeated probing requires review."
            ],

            "safeguards":
                [],

            "recommended_protocols": [
                "record_event",
                "increase_monitoring",
                "open_incident",
                "alert_administrator"
            ],

            "privilege_context": {
                "level": 0,
                "name": "standard",
                "role": "Financial Analyst"
            },

            "incident_state": {
                "event_count": 1,
                "security_assessment_count": 1,
                "consecutive_security_assessments": 1,
                "highest_severity_level": 4,
                "highest_response_level": 2,
                "last_classification": "suspicious",
                "existing_actions": []
            }
        }

        with tempfile.TemporaryDirectory() as (
            temporary_directory
        ):
            temporary_log = (
                Path(temporary_directory)
                / "central_telemetry.jsonl"
            )

            with patch(
                "hq.zenith_core."
                "CENTRAL_LOG_FILE",
                temporary_log
            ):
                (
                    central_event,
                    response
                ) = process_event(
                    event,
                    self.feature_engine,
                    self.inference_engine,
                    simulated_decision_engine,
                    self.protocol_executor
                )

        self.assertTrue(
            response[
                "protocols_executed"
            ]
        )

        self.assertIn(
            "zenith_execution",
            central_event
        )

        active_protocols = (
            self.state_store
            .active_protocols_for_event(
                event
            )
        )

        self.assertIn(
            "increase_monitoring",
            active_protocols
        )

        self.assertIn(
            "open_incident",
            active_protocols
        )

        self.assertIn(
            "alert_administrator",
            active_protocols
        )

if __name__ == "__main__":
    unittest.main()