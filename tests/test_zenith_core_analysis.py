import json
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

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
                    self.inference_engine
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


if __name__ == "__main__":
    unittest.main()