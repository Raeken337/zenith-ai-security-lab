import pandas as pd

from sklearn.model_selection import (
    train_test_split
)

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.compose import (
    ColumnTransformer
)

from sklearn.pipeline import (
    Pipeline
)

from sklearn.ensemble import (
    RandomForestClassifier
)

from sklearn.linear_model import (
    LogisticRegression
)

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score
)


DATASET_PATH = (
    "data/datasets/"
    "zenith_behaviour_dataset.csv"
)


dataset = pd.read_csv(
    DATASET_PATH
)


FEATURES = [
    "department",
    "role",
    "event_type",
    "hour",
    "failed_logins_10m",
    "denied_accesses_10m",
    "unique_resources_30m",
    "off_hours",
    "role_mismatch",
    "device_mismatch"
]


TARGET = "label"


X = dataset[FEATURES]
y = dataset[TARGET]


categorical_features = [
    "department",
    "role",
    "event_type"
]


numeric_features = [
    "hour",
    "failed_logins_10m",
    "denied_accesses_10m",
    "unique_resources_30m",
    "off_hours",
    "role_mismatch",
    "device_mismatch"
]


def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features
            ),
            (
                "numeric",
                StandardScaler(),
                numeric_features
            )
        ]
    )


random_forest_pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            build_preprocessor()
        ),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
        )
    ]
)


logistic_regression_pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            build_preprocessor()
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        )
    ]
)


X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
)


def evaluate_model(
    model_name,
    pipeline
):
    print(
        f"\n{model_name.upper()}"
    )

    print(
        "=" * len(model_name)
    )

    pipeline.fit(
        X_train,
        y_train
    )

    predictions = pipeline.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro"
    )

    weighted_f1 = f1_score(
        y_test,
        predictions,
        average="weighted"
    )

    print(
        f"\nAccuracy: "
        f"{accuracy:.4f}"
    )

    print(
        f"Macro F1: "
        f"{macro_f1:.4f}"
    )

    print(
        f"Weighted F1: "
        f"{weighted_f1:.4f}"
    )

    print(
        "\nClassification Report"
    )

    print(
        "---------------------"
    )

    print(
        classification_report(
            y_test,
            predictions
        )
    )

    print(
        "Confusion Matrix"
    )

    print(
        "----------------"
    )

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    return {
        "model": model_name,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1
    }


print(
    "\nZENITH BASELINE MODEL COMPARISON"
)

print(
    "================================"
)


random_forest_results = evaluate_model(
    "Random Forest",
    random_forest_pipeline
)


logistic_regression_results = evaluate_model(
    "Logistic Regression",
    logistic_regression_pipeline
)


comparison = pd.DataFrame([
    random_forest_results,
    logistic_regression_results
])


print(
    "\nMODEL COMPARISON"
)

print(
    "================"
)

print(
    comparison.to_string(
        index=False
    )
)