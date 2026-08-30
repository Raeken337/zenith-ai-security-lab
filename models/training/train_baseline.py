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


TARGET = "label"


FULL_FEATURES = [
    "department",
    "role",
    "event_type",

    "hour",
    "failed_logins_10m",
    "denied_accesses_10m",
    "unique_resources_30m",

    "off_hours",
    "role_mismatch",
    "device_mismatch",

    "recent_password_reset",
    "successful_recovery",

    "department_resource_mismatch",
    "resource_sensitivity",

    "recent_endpoints_used",
    "time_since_last_event_seconds",

    "sequence_pattern",

    "historical_user_deviation",
    "user_baseline_risk",

    "repeated_resource_accesses",
    "resource_traversal_count"
]


SELECTED_FEATURES = [
    "department",
    "role",
    "event_type",

    "hour",

    "failed_logins_10m",
    "denied_accesses_10m",
    "unique_resources_30m",

    "off_hours",

    "role_mismatch",
    "device_mismatch",

    "recent_password_reset",
    "successful_recovery",

    "department_resource_mismatch",
    "resource_sensitivity",

    "recent_endpoints_used",
    "time_since_last_event_seconds",

    "repeated_resource_accesses",
    "resource_traversal_count"
]


ALL_CATEGORICAL_FEATURES = [
    "department",
    "role",
    "event_type",
    "sequence_pattern"
]


ALL_NUMERIC_FEATURES = [
    "hour",

    "failed_logins_10m",
    "denied_accesses_10m",
    "unique_resources_30m",

    "off_hours",

    "role_mismatch",
    "device_mismatch",

    "recent_password_reset",
    "successful_recovery",

    "department_resource_mismatch",
    "resource_sensitivity",

    "recent_endpoints_used",
    "time_since_last_event_seconds",

    "historical_user_deviation",
    "user_baseline_risk",

    "repeated_resource_accesses",
    "resource_traversal_count"
]


X_full = dataset[
    FULL_FEATURES
]


X_selected = dataset[
    SELECTED_FEATURES
]


y = dataset[TARGET]


train_indices, test_indices = (
    train_test_split(
        dataset.index,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
)


X_full_train = X_full.loc[
    train_indices
]

X_full_test = X_full.loc[
    test_indices
]


X_selected_train = X_selected.loc[
    train_indices
]

X_selected_test = X_selected.loc[
    test_indices
]


y_train = y.loc[
    train_indices
]

y_test = y.loc[
    test_indices
]


def build_preprocessor(features):
    categorical_features = [
        feature
        for feature in ALL_CATEGORICAL_FEATURES
        if feature in features
    ]

    numeric_features = [
        feature
        for feature in ALL_NUMERIC_FEATURES
        if feature in features
    ]

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


def build_pipeline(
    classifier,
    features
):
    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(
                    features
                )
            ),
            (
                "classifier",
                classifier
            )
        ]
    )


def calculate_zenith_metrics(
    y_true,
    y_pred
):
    results = pd.DataFrame({
        "actual": y_true.values,
        "predicted": y_pred
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

    human_error_escalation_rate = (
        len(human_error_escalations)
        / len(human_error_cases)
        if len(human_error_cases) > 0
        else 0
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

    malicious_normal_miss_rate = (
        len(malicious_to_normal)
        / len(malicious_cases)
        if len(malicious_cases) > 0
        else 0
    )


    malicious_to_suspicious = (
        malicious_cases[
            malicious_cases[
                "predicted"
            ] == "suspicious"
        ]
    )

    malicious_suspicious_rate = (
        len(malicious_to_suspicious)
        / len(malicious_cases)
        if len(malicious_cases) > 0
        else 0
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

    suspicious_normal_miss_rate = (
        len(suspicious_to_normal)
        / len(suspicious_cases)
        if len(suspicious_cases) > 0
        else 0
    )


    security_relevant_cases = results[
        results["actual"].isin([
            "suspicious",
            "malicious"
        ])
    ]

    detected_security_cases = (
        security_relevant_cases[
            security_relevant_cases[
                "predicted"
            ].isin([
                "suspicious",
                "malicious"
            ])
        ]
    )

    security_detection_rate = (
        len(detected_security_cases)
        / len(security_relevant_cases)
        if len(security_relevant_cases) > 0
        else 0
    )


    return {
        "human_error_escalation_rate":
            human_error_escalation_rate,

        "malicious_normal_miss_rate":
            malicious_normal_miss_rate,

        "malicious_suspicious_rate":
            malicious_suspicious_rate,

        "suspicious_normal_miss_rate":
            suspicious_normal_miss_rate,

        "security_detection_rate":
            security_detection_rate
    }


def evaluate_model(
    model_name,
    pipeline,
    X_train,
    X_test,
    y_train,
    y_test
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

    zenith_metrics = (
        calculate_zenith_metrics(
            y_test,
            predictions
        )
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


    print(
        "\nZenith Security Metrics"
    )

    print(
        "-----------------------"
    )

    print(
        f"Human Error Escalation Rate: "
        f"{zenith_metrics['human_error_escalation_rate']:.2%}"
    )

    print(
        f"Malicious → Normal Miss Rate: "
        f"{zenith_metrics['malicious_normal_miss_rate']:.2%}"
    )

    print(
        f"Malicious → Suspicious Rate: "
        f"{zenith_metrics['malicious_suspicious_rate']:.2%}"
    )

    print(
        f"Suspicious → Normal Miss Rate: "
        f"{zenith_metrics['suspicious_normal_miss_rate']:.2%}"
    )

    print(
        f"Security Detection Rate: "
        f"{zenith_metrics['security_detection_rate']:.2%}"
    )


    return {
        "model": model_name,

        "accuracy":
            accuracy,

        "macro_f1":
            macro_f1,

        "weighted_f1":
            weighted_f1,

        "human_error_escalation":
            zenith_metrics[
                "human_error_escalation_rate"
            ],

        "malicious_normal_miss":
            zenith_metrics[
                "malicious_normal_miss_rate"
            ],

        "security_detection":
            zenith_metrics[
                "security_detection_rate"
            ]
    }


rf_full = build_pipeline(
    RandomForestClassifier(
        n_estimators=100,
        random_state=42
    ),
    FULL_FEATURES
)


rf_selected = build_pipeline(
    RandomForestClassifier(
        n_estimators=100,
        random_state=42
    ),
    SELECTED_FEATURES
)


lr_full = build_pipeline(
    LogisticRegression(
        max_iter=1000,
        random_state=42
    ),
    FULL_FEATURES
)


lr_selected = build_pipeline(
    LogisticRegression(
        max_iter=1000,
        random_state=42
    ),
    SELECTED_FEATURES
)


print(
    "\nZENITH FEATURE SELECTION TEST"
)

print(
    "============================="
)


results = []


results.append(
    evaluate_model(
        "Random Forest - Full",
        rf_full,
        X_full_train,
        X_full_test,
        y_train,
        y_test
    )
)


results.append(
    evaluate_model(
        "Random Forest - Selected",
        rf_selected,
        X_selected_train,
        X_selected_test,
        y_train,
        y_test
    )
)


results.append(
    evaluate_model(
        "Logistic Regression - Full",
        lr_full,
        X_full_train,
        X_full_test,
        y_train,
        y_test
    )
)


results.append(
    evaluate_model(
        "Logistic Regression - Selected",
        lr_selected,
        X_selected_train,
        X_selected_test,
        y_train,
        y_test
    )
)


comparison = pd.DataFrame(
    results
)


print(
    "\nFEATURE SELECTION COMPARISON"
)

print(
    "============================"
)

print(
    comparison.to_string(
        index=False
    )
)