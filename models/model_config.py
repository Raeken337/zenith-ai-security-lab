MODEL_VERSION = "1.0.0"

FEATURE_SCHEMA_VERSION = "1.0"


RANDOM_FOREST_WEIGHT = 0.90

LOGISTIC_REGRESSION_WEIGHT = 0.10


MODEL_ROLES = {
    "random_forest": "primary",
    "logistic_regression": "supporting"
}


EXPECTED_CLASSES = [
    "human_error",
    "malicious",
    "normal",
    "suspicious"
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


FEATURE_GROUPS = {
    "authentication_recovery": [
        "event_type",
        "failed_logins_10m",
        "recent_password_reset",
        "successful_recovery"
    ],

    "identity_role": [
        "department",
        "role",
        "role_mismatch"
    ],

    "resource_context": [
        "denied_accesses_10m",
        "unique_resources_30m",
        "department_resource_mismatch",
        "resource_sensitivity"
    ],

    "endpoint_context": [
        "device_mismatch",
        "recent_endpoints_used"
    ],

    "temporal_context": [
        "hour",
        "off_hours",
        "time_since_last_event_seconds"
    ],

    "traversal_context": [
        "repeated_resource_accesses",
        "resource_traversal_count"
    ]
}


CATEGORICAL_FEATURES = [
    "department",
    "role",
    "event_type"
]


NUMERIC_FEATURES = [
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