import json
import math

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from models.model_config import (
    CATEGORICAL_FEATURES,
    EXPECTED_CLASSES,
    LOGISTIC_REGRESSION_WEIGHT,
    NUMERIC_FEATURES,
    RANDOM_FOREST_WEIGHT,
    SELECTED_FEATURES
)


DEFAULT_MODEL_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "saved_models"
)


METADATA_FILENAME = (
    "zenith_v1_metadata.json"
)


SECURITY_CLASSES = {
    "suspicious",
    "malicious"
}


class ZenithInferenceEngine:
    def __init__(
        self,
        model_directory=None
    ):
        self.model_directory = Path(
            model_directory
            or DEFAULT_MODEL_DIRECTORY
        )

        self.metadata = (
            self._load_metadata()
        )

        self._validate_metadata()

        self.random_forest = (
            self._load_model(
                "random_forest"
            )
        )

        self.logistic_regression = (
            self._load_model(
                "logistic_regression"
            )
        )

        self.classes = list(
            self.metadata["classes"]
        )

        self._validate_models()

    def assess(self, features):
        self._validate_features(
            features
        )

        feature_frame = pd.DataFrame([
            {
                feature: features[feature]
                for feature in SELECTED_FEATURES
            }
        ])

        random_forest_probabilities = (
            self.random_forest.predict_proba(
                feature_frame
            )[0]
        )

        logistic_regression_probabilities = (
            self.logistic_regression.predict_proba(
                feature_frame
            )[0]
        )

        combined_probabilities = (
            random_forest_probabilities
            * RANDOM_FOREST_WEIGHT
            + logistic_regression_probabilities
            * LOGISTIC_REGRESSION_WEIGHT
        )

        random_forest_result = (
            self._build_model_result(
                random_forest_probabilities
            )
        )

        logistic_regression_result = (
            self._build_model_result(
                logistic_regression_probabilities
            )
        )

        combined_result = (
            self._build_model_result(
                combined_probabilities
            )
        )

        agreement_level = (
            self._calculate_agreement_level(
                random_forest_result[
                    "classification"
                ],
                logistic_regression_result[
                    "classification"
                ]
            )
        )

        sorted_probabilities = sorted(
            combined_result[
                "probabilities"
            ].values(),
            reverse=True
        )

        confidence_gap = (
            sorted_probabilities[0]
            - sorted_probabilities[1]
        )

        return {
            "classification":
                combined_result[
                    "classification"
                ],

            "confidence":
                combined_result[
                    "confidence"
                ],

            "confidence_gap":
                float(confidence_gap),

            "agreement":
                agreement_level,

            "security_disagreement": (
                self._has_security_disagreement(
                    random_forest_result[
                        "classification"
                    ],
                    logistic_regression_result[
                        "classification"
                    ]
                )
            ),

            "combined_probabilities":
                combined_result[
                    "probabilities"
                ],

            "models": {
                "random_forest": {
                    "role": "primary",
                    "weight":
                        RANDOM_FOREST_WEIGHT,

                    **random_forest_result
                },

                "logistic_regression": {
                    "role": "supporting",
                    "weight":
                        LOGISTIC_REGRESSION_WEIGHT,

                    **logistic_regression_result
                }
            },

            "feature_snapshot": {
                feature: features[feature]
                for feature in SELECTED_FEATURES
            },

            "model_version":
                self.metadata[
                    "model_version"
                ],

            "feature_schema_version":
                self.metadata[
                    "feature_schema_version"
                ]
        }

    def _load_metadata(self):
        metadata_path = (
            self.model_directory
            / METADATA_FILENAME
        )

        if not metadata_path.exists():
            raise FileNotFoundError(
                "Zenith model metadata was not found: "
                f"{metadata_path}"
            )

        with metadata_path.open(
            "r",
            encoding="utf-8"
        ) as metadata_file:
            return json.load(
                metadata_file
            )

    def _load_model(
        self,
        model_name
    ):
        model_filename = (
            self.metadata[
                "models"
            ][model_name]["file"]
        )

        model_path = (
            self.model_directory
            / model_filename
        )

        if not model_path.exists():
            raise FileNotFoundError(
                "Zenith model was not found: "
                f"{model_path}"
            )

        return joblib.load(
            model_path
        )

    def _validate_metadata(self):
        metadata_features = (
            self.metadata.get(
                "feature_schema"
            )
        )

        if metadata_features != SELECTED_FEATURES:
            raise ValueError(
                "Saved model feature schema does "
                "not match model_config.py."
            )

        metadata_classes = (
            self.metadata.get(
                "classes"
            )
        )

        if metadata_classes != EXPECTED_CLASSES:
            raise ValueError(
                "Saved model classes do not match "
                "model_config.py."
            )

        metadata_models = (
            self.metadata.get(
                "models",
                {}
            )
        )

        random_forest_weight = (
            metadata_models.get(
                "random_forest",
                {}
            ).get(
                "weight"
            )
        )

        logistic_regression_weight = (
            metadata_models.get(
                "logistic_regression",
                {}
            ).get(
                "weight"
            )
        )

        if not math.isclose(
            random_forest_weight,
            RANDOM_FOREST_WEIGHT
        ):
            raise ValueError(
                "Random Forest weight does not "
                "match the saved metadata."
            )

        if not math.isclose(
            logistic_regression_weight,
            LOGISTIC_REGRESSION_WEIGHT
        ):
            raise ValueError(
                "Logistic Regression weight does "
                "not match the saved metadata."
            )

        if not math.isclose(
            (
                RANDOM_FOREST_WEIGHT
                + LOGISTIC_REGRESSION_WEIGHT
            ),
            1.0
        ):
            raise ValueError(
                "Model weights must total 1.0."
            )

    def _validate_models(self):
        for model_name, model in [
            (
                "Random Forest",
                self.random_forest
            ),
            (
                "Logistic Regression",
                self.logistic_regression
            )
        ]:
            classifier = model.named_steps[
                "classifier"
            ]

            model_classes = list(
                classifier.classes_
            )

            if model_classes != self.classes:
                raise ValueError(
                    f"{model_name} class order "
                    "does not match metadata."
                )

            feature_names = list(
                model.feature_names_in_
            )

            if feature_names != SELECTED_FEATURES:
                raise ValueError(
                    f"{model_name} feature order "
                    "does not match model_config.py."
                )

    def _validate_features(
        self,
        features
    ):
        expected_features = set(
            SELECTED_FEATURES
        )

        actual_features = set(
            features
        )

        if actual_features != expected_features:
            raise ValueError({
                "missing_features":
                    sorted(
                        expected_features
                        - actual_features
                    ),

                "unexpected_features":
                    sorted(
                        actual_features
                        - expected_features
                    )
            })

        for feature in CATEGORICAL_FEATURES:
            value = features[feature]

            if (
                not isinstance(
                    value,
                    str
                )
                or not value
            ):
                raise ValueError(
                    f"{feature} must be a "
                    "non-empty string."
                )

        for feature in NUMERIC_FEATURES:
            value = features[feature]

            if not isinstance(
                value,
                (
                    int,
                    float,
                    np.integer,
                    np.floating
                )
            ):
                raise ValueError(
                    f"{feature} must be numeric."
                )

            if not np.isfinite(
                value
            ):
                raise ValueError(
                    f"{feature} must be finite."
                )

    def _build_model_result(
        self,
        probabilities
    ):
        probability_map = {
            class_name: float(
                probability
            )
            for class_name, probability
            in zip(
                self.classes,
                probabilities
            )
        }

        predicted_index = int(
            np.argmax(
                probabilities
            )
        )

        classification = self.classes[
            predicted_index
        ]

        return {
            "classification":
                classification,

            "confidence":
                float(
                    probabilities[
                        predicted_index
                    ]
                ),

            "probabilities":
                probability_map
        }

    def _calculate_agreement_level(
        self,
        random_forest_class,
        logistic_regression_class
    ):
        if (
            random_forest_class
            == logistic_regression_class
        ):
            return "high"

        random_forest_security = (
            random_forest_class
            in SECURITY_CLASSES
        )

        logistic_regression_security = (
            logistic_regression_class
            in SECURITY_CLASSES
        )

        if (
            random_forest_security
            == logistic_regression_security
        ):
            return "moderate"

        return "low"

    def _has_security_disagreement(
        self,
        random_forest_class,
        logistic_regression_class
    ):
        return (
            (
                random_forest_class
                in SECURITY_CLASSES
            )
            !=
            (
                logistic_regression_class
                in SECURITY_CLASSES
            )
        )