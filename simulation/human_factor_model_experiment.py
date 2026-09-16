from models.runtime.feature_engine import (
    FeatureEngine
)

from models.runtime.inference_engine import (
    ZenithInferenceEngine
)


def build_event(
    timestamp,
    event_type,
    resource=None,
    source_device="PC-FIN-01"
):
    event = {
        "timestamp": timestamp,
        "event_type": event_type,
        "username": "jake",
        "department": "finance",
        "role": "Financial Analyst",
        "source_device": source_device
    }

    if resource is not None:
        event["resource"] = resource

    return event


SCENARIOS = [
    {
        "name": "Normal Finance Activity",

        "expected_behaviour": (
            "Normal activity should remain "
            "non-security-relevant."
        ),

        "events": [
            build_event(
                "2026-09-17T09:00:00",
                "login_success"
            ),

            build_event(
                "2026-09-17T09:02:00",
                "file_access_success",
                resource="finance_reports"
            )
        ]
    },

    {
        "name": "Password Reset Recovery",

        "expected_behaviour": (
            "Repeated mistakes followed by a "
            "reset and legitimate work should "
            "look like human error or recovery."
        ),

        "events": [
            build_event(
                "2026-09-17T09:00:00",
                "login_failure"
            ),

            build_event(
                "2026-09-17T09:01:00",
                "login_failure"
            ),

            build_event(
                "2026-09-17T09:02:00",
                "password_reset"
            ),

            build_event(
                "2026-09-17T09:03:00",
                "login_success"
            ),

            build_event(
                "2026-09-17T09:05:00",
                "file_access_success",
                resource="finance_reports"
            )
        ]
    },

    {
        "name": "Single Access Mistake",

        "expected_behaviour": (
            "One incorrect resource followed by "
            "normal work should be investigated "
            "lightly without containment."
        ),

        "events": [
            build_event(
                "2026-09-17T09:00:00",
                "login_success"
            ),

            build_event(
                "2026-09-17T09:02:00",
                "file_access_denied",
                resource="hr_records"
            ),

            build_event(
                "2026-09-17T09:04:00",
                "file_access_success",
                resource="finance_reports"
            )
        ]
    },

    {
        "name": "Suspicious Post-Login Access",

        "expected_behaviour": (
            "Login recovery followed immediately "
            "by unauthorised access should raise "
            "suspicion."
        ),

        "events": [
            build_event(
                "2026-09-17T09:00:00",
                "login_failure"
            ),

            build_event(
                "2026-09-17T09:01:00",
                "login_failure"
            ),

            build_event(
                "2026-09-17T09:02:00",
                "login_success"
            ),

            build_event(
                "2026-09-17T09:03:00",
                "file_access_denied",
                resource="hr_records"
            )
        ]
    },

    {
        "name": "Repeated Resource Probing",

        "expected_behaviour": (
            "Repeated cross-department probing "
            "should become security-relevant."
        ),

        "events": [
            build_event(
                "2026-09-17T09:00:00",
                "login_failure"
            ),

            build_event(
                "2026-09-17T09:01:00",
                "login_failure"
            ),

            build_event(
                "2026-09-17T09:02:00",
                "login_success"
            ),

            build_event(
                "2026-09-17T09:03:00",
                "file_access_denied",
                resource="hr_records"
            ),

            build_event(
                "2026-09-17T09:04:00",
                "file_access_denied",
                resource="employee_records"
            ),

            build_event(
                "2026-09-17T09:05:00",
                "file_access_denied",
                resource="remote_admin"
            )
        ]
    },

    {
        "name": "Unexpected Endpoint Switch",

        "expected_behaviour": (
            "Using another employee's endpoint "
            "should produce security evidence."
        ),

        "events": [
            build_event(
                "2026-09-17T09:00:00",
                "login_success"
            ),

            build_event(
                "2026-09-17T09:01:00",
                "file_access_success",
                resource="finance_reports",
                source_device="PC-HR-01"
            )
        ]
    }
]


def format_percentage(value):
    return f"{value:.1%}"


def display_step(
    step_number,
    event,
    features,
    assessment
):
    random_forest = assessment[
        "models"
    ][
        "random_forest"
    ]

    logistic_regression = assessment[
        "models"
    ][
        "logistic_regression"
    ]

    resource = event.get(
        "resource",
        "-"
    )

    print(
        f"\nStep {step_number}: "
        f"{event['event_type']}"
    )

    print(
        f"Resource: {resource}"
    )

    print(
        "RF: "
        f"{random_forest['classification']} "
        f"({format_percentage(random_forest['confidence'])})"
    )

    print(
        "LR: "
        f"{logistic_regression['classification']} "
        f"({format_percentage(logistic_regression['confidence'])})"
    )

    print(
        "Combined: "
        f"{assessment['classification']} "
        f"({format_percentage(assessment['confidence'])})"
    )

    print(
        f"Agreement: "
        f"{assessment['agreement']}"
    )

    print(
        "Evidence: "
        f"failures={features['failed_logins_10m']}, "
        f"denials={features['denied_accesses_10m']}, "
        f"resources={features['unique_resources_30m']}, "
        f"endpoints={features['recent_endpoints_used']}, "
        f"recovery={features['successful_recovery']}, "
        f"resource_mismatch="
        f"{features['department_resource_mismatch']}, "
        f"device_mismatch="
        f"{features['device_mismatch']}, "
        f"traversal="
        f"{features['resource_traversal_count']}"
    )


def run_scenario(
    scenario,
    inference_engine
):
    feature_engine = FeatureEngine()

    print(
        "\n"
        + "=" * 70
    )

    print(
        scenario["name"].upper()
    )

    print(
        "=" * 70
    )

    print(
        "Expected: "
        f"{scenario['expected_behaviour']}"
    )

    final_assessment = None

    for step_number, event in enumerate(
        scenario["events"],
        start=1
    ):
        features = (
            feature_engine.process_event(
                event
            )
        )

        final_assessment = (
            inference_engine.assess(
                features
            )
        )

        display_step(
            step_number,
            event,
            features,
            final_assessment
        )

    return {
        "scenario": scenario["name"],

        "classification":
            final_assessment[
                "classification"
            ],

        "confidence":
            final_assessment[
                "confidence"
            ],

        "agreement":
            final_assessment[
                "agreement"
            ],

        "security_disagreement":
            final_assessment[
                "security_disagreement"
            ]
    }


def display_summary(results):
    print(
        "\n"
        + "=" * 70
    )

    print(
        "HUMAN-FACTOR MODEL SUMMARY"
    )

    print(
        "=" * 70
    )

    for result in results:
        print(
            f"\n{result['scenario']}"
        )

        print(
            "  Final classification: "
            f"{result['classification']}"
        )

        print(
            "  Confidence: "
            f"{format_percentage(result['confidence'])}"
        )

        print(
            "  Agreement: "
            f"{result['agreement']}"
        )

        print(
            "  Security disagreement: "
            f"{result['security_disagreement']}"
        )


def main():
    inference_engine = (
        ZenithInferenceEngine()
    )

    results = []

    for scenario in SCENARIOS:
        results.append(
            run_scenario(
                scenario,
                inference_engine
            )
        )

    display_summary(
        results
    )


if __name__ == "__main__":
    main()