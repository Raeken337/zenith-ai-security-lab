import hashlib
import json
import platform

from datetime import (
    datetime,
    timezone
)

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.compose import (
    ColumnTransformer
)

from sklearn.ensemble import (
    RandomForestClassifier
)

from sklearn.linear_model import (
    LogisticRegression
)

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)

from sklearn.model_selection import (
    train_test_split
)

from sklearn.pipeline import (
    Pipeline
)

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from models.model_config import (
    CATEGORICAL_FEATURES,
    EXPECTED_CLASSES,
    FEATURE_GROUPS,
    FEATURE_SCHEMA_VERSION,
    LOGISTIC_REGRESSION_WEIGHT,
    MODEL_ROLES,
    MODEL_VERSION,
    NUMERIC_FEATURES,
    RANDOM_FOREST_WEIGHT,
    SELECTED_FEATURES
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "datasets"
    / "zenith_behaviour_dataset.csv"
)


MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "models"
    / "saved_models"
)


RANDOM_FOREST_MODEL_PATH = (
    MODEL_DIRECTORY
    / "zenith_rf_v1.joblib"
)


LOGISTIC_REGRESSION_MODEL_PATH = (
    MODEL_DIRECTORY
    / "zenith_lr_v1.joblib"
)


METADATA_PATH = (
    MODEL_DIRECTORY
    / "zenith_v1_metadata.json"
)


TARGET = "label"

TEST_SIZE = 0.20

RANDOM_STATE = 42


def calculate_file_sha256(file_path):
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        while True:
            block = file.read(65536)

            if not block:
                break

            sha256.update(block)

    return sha256.hexdigest()


def validate_dataset(dataset):
    required_columns = (
        set(SELECTED_FEATURES)
        | {TARGET}
    )

    missing_columns = (
        required_columns
        - set(dataset.columns)
    )

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    unexpected_classes = (
        set(dataset[TARGET].unique())
        - set(EXPECTED_CLASSES)
    )

    if unexpected_classes:
        raise ValueError(
            "Dataset contains unexpected classes: "
            f"{sorted(unexpected_classes)}"
        )


def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CATEGORICAL_FEATURES
            ),
            (
                "numeric",
                StandardScaler(),
                NUMERIC_FEATURES
            )
        ]
    )


def build_random_forest_pipeline():
    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor()
            ),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=100,
                    random_state=RANDOM_STATE
                )
            )
        ]
    )


def build_logistic_regression_pipeline():
    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor()
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=RANDOM_STATE
                )
            )
        ]
    )


def calculate_zenith_metrics(
    y_true,
    predictions
):
    results = pd.DataFrame({
        "actual": list(y_true),
        "predicted": list(predictions)
    })

    human_error_cases = results[
        results["actual"] == "human_error"
    ]

    human_error_escalations = (
        human_error_cases[
            human_error_cases[
                "predicted"
            ].isin([
                "suspicious",
                "malicious"
            ])
        ]
    )

    malicious_cases = results[
        results["actual"] == "malicious"
    ]

    malicious_to_normal = (
        malicious_cases[
            malicious_cases[
                "predicted"
            ] == "normal"
        ]
    )

    malicious_to_suspicious = (
        malicious_cases[
            malicious_cases[
                "predicted"
            ] == "suspicious"
        ]
    )

    suspicious_cases = results[
        results["actual"] == "suspicious"
    ]

    suspicious_to_normal = (
        suspicious_cases[
            suspicious_cases[
                "predicted"
            ] == "normal"
        ]
    )

    security_cases = results[
        results["actual"].isin([
            "suspicious",
            "malicious"
        ])
    ]

    detected_security_cases = (
        security_cases[
            security_cases[
                "predicted"
            ].isin([
                "suspicious",
                "malicious"
            ])
        ]
    )

    return {
        "human_error_escalation_rate": (
            len(human_error_escalations)
            / len(human_error_cases)
            if len(human_error_cases)
            else 0
        ),

        "malicious_normal_miss_rate": (
            len(malicious_to_normal)
            / len(malicious_cases)
            if len(malicious_cases)
            else 0
        ),

        "malicious_suspicious_rate": (
            len(malicious_to_suspicious)
            / len(malicious_cases)
            if len(malicious_cases)
            else 0
        ),

        "suspicious_normal_miss_rate": (
            len(suspicious_to_normal)
            / len(suspicious_cases)
            if len(suspicious_cases)
            else 0
        ),

        "security_detection_rate": (
            len(detected_security_cases)
            / len(security_cases)
            if len(security_cases)
            else 0
        )
    }


def evaluate_predictions(
    y_true,
    predictions
):
    return {
        "accuracy": accuracy_score(
            y_true,
            predictions
        ),

        "macro_f1": f1_score(
            y_true,
            predictions,
            average="macro"
        ),

        "weighted_f1": f1_score(
            y_true,
            predictions,
            average="weighted"
        ),

        "zenith_metrics":
            calculate_zenith_metrics(
                y_true,
                predictions
            ),

        "confusion_matrix":
            confusion_matrix(
                y_true,
                predictions,
                labels=EXPECTED_CLASSES
            ).tolist(),

        "classification_report":
            classification_report(
                y_true,
                predictions,
                labels=EXPECTED_CLASSES,
                output_dict=True,
                zero_division=0
            )
    }


def validate_model_classes(
    random_forest_pipeline,
    logistic_regression_pipeline
):
    random_forest_classes = list(
        random_forest_pipeline.named_steps[
            "classifier"
        ].classes_
    )

    logistic_regression_classes = list(
        logistic_regression_pipeline.named_steps[
            "classifier"
        ].classes_
    )

    if random_forest_classes != EXPECTED_CLASSES:
        raise ValueError(
            "Random Forest classes do not match "
            "the configured class order."
        )

    if logistic_regression_classes != EXPECTED_CLASSES:
        raise ValueError(
            "Logistic Regression classes do not "
            "match the configured class order."
        )

    return random_forest_classes


def evaluate_models(
    X_train,
    X_test,
    y_train,
    y_test
):
    random_forest_pipeline = (
        build_random_forest_pipeline()
    )

    logistic_regression_pipeline = (
        build_logistic_regression_pipeline()
    )

    random_forest_pipeline.fit(
        X_train,
        y_train
    )

    logistic_regression_pipeline.fit(
        X_train,
        y_train
    )

    classes = validate_model_classes(
        random_forest_pipeline,
        logistic_regression_pipeline
    )

    random_forest_predictions = (
        random_forest_pipeline.predict(
            X_test
        )
    )

    logistic_regression_predictions = (
        logistic_regression_pipeline.predict(
            X_test
        )
    )

    random_forest_probabilities = (
        random_forest_pipeline.predict_proba(
            X_test
        )
    )

    logistic_regression_probabilities = (
        logistic_regression_pipeline.predict_proba(
            X_test
        )
    )

    combined_probabilities = (
        random_forest_probabilities
        * RANDOM_FOREST_WEIGHT
        + logistic_regression_probabilities
        * LOGISTIC_REGRESSION_WEIGHT
    )

    combined_predictions = np.array(
        classes
    )[
        np.argmax(
            combined_probabilities,
            axis=1
        )
    ]

    return {
        "random_forest":
            evaluate_predictions(
                y_test,
                random_forest_predictions
            ),

        "logistic_regression":
            evaluate_predictions(
                y_test,
                logistic_regression_predictions
            ),

        "weighted_ensemble":
            evaluate_predictions(
                y_test,
                combined_predictions
            )
    }


def train_final_models(
    X,
    y
):
    random_forest_pipeline = (
        build_random_forest_pipeline()
    )

    logistic_regression_pipeline = (
        build_logistic_regression_pipeline()
    )

    random_forest_pipeline.fit(
        X,
        y
    )

    logistic_regression_pipeline.fit(
        X,
        y
    )

    classes = validate_model_classes(
        random_forest_pipeline,
        logistic_regression_pipeline
    )

    return (
        random_forest_pipeline,
        logistic_regression_pipeline,
        classes
    )


def save_models(
    random_forest_pipeline,
    logistic_regression_pipeline
):
    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        random_forest_pipeline,
        RANDOM_FOREST_MODEL_PATH,
        compress=3
    )

    joblib.dump(
        logistic_regression_pipeline,
        LOGISTIC_REGRESSION_MODEL_PATH,
        compress=3
    )


def build_metadata(
    dataset,
    classes,
    evaluation_results
):
    return {
        "model_version":
            MODEL_VERSION,

        "feature_schema_version":
            FEATURE_SCHEMA_VERSION,

        "created_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "training": {
            "dataset_path": str(
                DATASET_PATH.relative_to(
                    PROJECT_ROOT
                )
            ),

            "dataset_sha256":
                calculate_file_sha256(
                    DATASET_PATH
                ),

            "row_count":
                len(dataset),

            "target":
                TARGET,

            "random_state":
                RANDOM_STATE,

            "evaluation_test_size":
                TEST_SIZE,

            "final_training_scope":
                "all_dataset_rows"
        },

        "feature_schema":
            SELECTED_FEATURES,

        "feature_groups":
            FEATURE_GROUPS,

        "classes":
            classes,

        "models": {
            "random_forest": {
                "role":
                    MODEL_ROLES[
                        "random_forest"
                    ],

                "weight":
                    RANDOM_FOREST_WEIGHT,

                "file":
                    RANDOM_FOREST_MODEL_PATH.name,

                "parameters": {
                    "n_estimators": 100,
                    "random_state":
                        RANDOM_STATE
                }
            },

            "logistic_regression": {
                "role":
                    MODEL_ROLES[
                        "logistic_regression"
                    ],

                "weight":
                    LOGISTIC_REGRESSION_WEIGHT,

                "file":
                    LOGISTIC_REGRESSION_MODEL_PATH.name,

                "parameters": {
                    "max_iter": 1000,
                    "random_state":
                        RANDOM_STATE
                }
            }
        },

        "evaluation":
            evaluation_results,

        "runtime_versions": {
            "python":
                platform.python_version(),

            "pandas":
                pd.__version__,

            "scikit_learn":
                sklearn.__version__,

            "joblib":
                joblib.__version__,

            "numpy":
                np.__version__
        },

        "limitations": [
            (
                "Models are trained using "
                "synthetic behavioural data."
            ),
            (
                "Model probabilities are not "
                "validated production risk scores."
            ),
            (
                "The 90/10 model weighting was "
                "selected using the current "
                "experimental test split."
            ),
            (
                "Final exported pipelines are "
                "retrained using all dataset rows."
            )
        ]
    }


def save_metadata(metadata):
    with METADATA_PATH.open(
        "w",
        encoding="utf-8"
    ) as metadata_file:
        json.dump(
            metadata,
            metadata_file,
            indent=4
        )


def print_summary(
    dataset,
    evaluation_results
):
    print(
        "\nZENITH V1 MODELS EXPORTED"
    )

    print(
        "========================="
    )

    print(
        f"Training rows: {len(dataset)}"
    )

    print(
        f"Feature count: "
        f"{len(SELECTED_FEATURES)}"
    )

    print(
        f"Random Forest weight: "
        f"{RANDOM_FOREST_WEIGHT:.0%}"
    )

    print(
        f"Logistic Regression weight: "
        f"{LOGISTIC_REGRESSION_WEIGHT:.0%}"
    )

    print(
        "\nWeighted Ensemble Evaluation"
    )

    print(
        "----------------------------"
    )

    ensemble_results = (
        evaluation_results[
            "weighted_ensemble"
        ]
    )

    print(
        f"Accuracy: "
        f"{ensemble_results['accuracy']:.2%}"
    )

    print(
        f"Macro F1: "
        f"{ensemble_results['macro_f1']:.2%}"
    )

    print(
        "Security Detection: "
        f"{ensemble_results['zenith_metrics']['security_detection_rate']:.2%}"
    )

    print(
        "Human Error Escalation: "
        f"{ensemble_results['zenith_metrics']['human_error_escalation_rate']:.2%}"
    )

    print(
        "\nSaved files:"
    )

    print(
        f"- {RANDOM_FOREST_MODEL_PATH}"
    )

    print(
        f"- {LOGISTIC_REGRESSION_MODEL_PATH}"
    )

    print(
        f"- {METADATA_PATH}"
    )


def main():
    dataset = pd.read_csv(
        DATASET_PATH
    )

    validate_dataset(
        dataset
    )

    X = dataset[
        SELECTED_FEATURES
    ]

    y = dataset[
        TARGET
    ]

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )

    evaluation_results = evaluate_models(
        X_train,
        X_test,
        y_train,
        y_test
    )

    (
        random_forest_pipeline,
        logistic_regression_pipeline,
        classes
    ) = train_final_models(
        X,
        y
    )

    save_models(
        random_forest_pipeline,
        logistic_regression_pipeline
    )

    metadata = build_metadata(
        dataset,
        classes,
        evaluation_results
    )

    save_metadata(
        metadata
    )

    print_summary(
        dataset,
        evaluation_results
    )


if __name__ == "__main__":
    main()