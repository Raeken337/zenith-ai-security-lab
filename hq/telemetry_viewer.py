import json
import time
from pathlib import Path


CENTRAL_LOG_FILE = Path(
    "data/logs/central_telemetry.jsonl"
)


def load_events():
    if not CENTRAL_LOG_FILE.exists():
        return []

    events = []

    with CENTRAL_LOG_FILE.open(
        "r",
        encoding="utf-8"
    ) as log_file:

        for line in log_file:
            line = line.strip()

            if not line:
                continue

            event = json.loads(line)
            events.append(event)

    return events

def format_label(value):
    if value is None:
        return "Unknown"

    return str(
        value
    ).replace(
        "_",
        " "
    ).title()


def format_percentage(value):
    if value is None:
        return "Unknown"

    return f"{value:.2%}"


def describe_event(event):
    event_type = event.get(
        "event_type"
    )

    username = event.get(
        "username",
        "unknown user"
    )

    source_device = event.get(
        "source_device",
        "unknown device"
    )

    resource = event.get(
        "resource"
    )

    descriptions = {
        "login_success": (
            f"{username} successfully authenticated "
            f"from {source_device}."
        ),

        "login_failure": (
            f"{username} failed to authenticate "
            f"from {source_device}."
        ),

        "account_locked": (
            f"{username}'s account was locked "
            "after repeated authentication failures."
        ),

        "password_reset": (
            f"{username} completed a password reset."
        ),

        "password_reset_denied": (
            f"A password reset for {username} "
            "was denied."
        ),

        "file_access_success": (
            f"{username} accessed "
            f"{format_label(resource)} "
            f"from {source_device}."
        ),

        "file_access_denied": (
            f"{username} was denied access to "
            f"{format_label(resource)} "
            f"from {source_device}."
        )
    }

    return descriptions.get(
        event_type,
        (
            f"{username} generated a "
            f"{format_label(event_type)} event."
        )
    )


def display_feature_evidence(features):
    print(
        "\nBehavioural Evidence"
    )

    print(
        "--------------------"
    )

    print(
        "Recent window: "
        f"{features.get('failed_logins_10m', 0)} "
        "failed login(s), "
        f"{features.get('denied_accesses_10m', 0)} "
        "denied access(es), "
        f"{features.get('unique_resources_30m', 0)} "
        "unique resource(s), "
        f"{features.get('recent_endpoints_used', 0)} "
        "endpoint(s)"
    )

    print(
        "Movement: "
        f"{features.get('resource_traversal_count', 0)} "
        "traversal step(s), "
        f"{features.get('repeated_resource_accesses', 0)} "
        "repeated access(es)"
    )

    notable_evidence = []

    failed_logins = features.get(
        "failed_logins_10m",
        0
    )

    if failed_logins:
        notable_evidence.append(
            f"{failed_logins} failed login(s) "
            "during the last 10 minutes"
        )

    denied_accesses = features.get(
        "denied_accesses_10m",
        0
    )

    if denied_accesses:
        notable_evidence.append(
            f"{denied_accesses} denied resource "
            "request(s) during the last 10 minutes"
        )

    if features.get(
        "off_hours"
    ):
        notable_evidence.append(
            "activity occurred outside the "
            "user's expected working hours"
        )

    if features.get(
        "role_mismatch"
    ):
        notable_evidence.append(
            "the supplied role or department "
            "does not match the user directory"
        )

    if features.get(
        "device_mismatch"
    ):
        notable_evidence.append(
            "the source endpoint is not assigned "
            "to this user"
        )

    if features.get(
        "recent_password_reset"
    ):
        notable_evidence.append(
            "a recent password reset is present"
        )

    if features.get(
        "successful_recovery"
    ):
        notable_evidence.append(
            "successful recovery after an "
            "authentication problem is present"
        )

    if features.get(
        "department_resource_mismatch"
    ):
        notable_evidence.append(
            "the current resource belongs to "
            "another department"
        )

    resource_sensitivity = features.get(
        "resource_sensitivity",
        0
    )

    if resource_sensitivity:
        notable_evidence.append(
            "current resource sensitivity is "
            f"{resource_sensitivity}/5"
        )

    endpoint_count = features.get(
        "recent_endpoints_used",
        0
    )

    if endpoint_count > 1:
        notable_evidence.append(
            f"activity has used {endpoint_count} "
            "different endpoints"
        )

    traversal_count = features.get(
        "resource_traversal_count",
        0
    )

    if traversal_count > 1:
        notable_evidence.append(
            "movement across "
            f"{traversal_count} resources "
            "has been observed"
        )

    print(
        "\nNotable context:"
    )

    if not notable_evidence:
        print(
            "- No elevated contextual "
            "indicators observed."
        )

    else:
        for evidence in notable_evidence:
            print(
                f"- {evidence}"
            )

    time_since_event = features.get(
        "time_since_last_event_seconds"
    )

    if time_since_event is not None:
        print(
            "- Time since previous event: "
            f"{time_since_event} second(s)"
        )


def display_model_opinion(
    model_name,
    model_result
):
    print(
        f"{model_name}: "
        f"{format_label(model_result.get('classification'))} "
        f"({format_percentage(model_result.get('confidence'))})"
    )


def display_assessment(assessment):
    print(
        "\nZenith Analysis"
    )

    print(
        "---------------"
    )

    models = assessment.get(
        "models",
        {}
    )

    random_forest = models.get(
        "random_forest",
        {}
    )

    logistic_regression = models.get(
        "logistic_regression",
        {}
    )

    display_model_opinion(
        "Random Forest - Primary",
        random_forest
    )

    display_model_opinion(
        "Logistic Regression - Supporting",
        logistic_regression
    )

    print(
        "\nCombined assessment: "
        f"{format_label(assessment.get('classification'))} "
        f"({format_percentage(assessment.get('confidence'))})"
    )

    print(
        "Model agreement: "
        f"{format_label(assessment.get('agreement'))}"
    )

    print(
        "Confidence gap: "
        f"{format_percentage(assessment.get('confidence_gap'))}"
    )

    if assessment.get(
        "security_disagreement"
    ):
        print(
            "WARNING: The models disagree on "
            "whether this activity is "
            "security-relevant."
        )

    combined_probabilities = assessment.get(
        "combined_probabilities",
        {}
    )

    if combined_probabilities:
        print(
            "\nCombined probabilities:"
        )

        sorted_probabilities = sorted(
            combined_probabilities.items(),
            key=lambda item: item[1],
            reverse=True
        )

        for class_name, probability in (
            sorted_probabilities
        ):
            print(
                f"- {format_label(class_name)}: "
                f"{format_percentage(probability)}"
            )


def display_event(
    event,
    number=None
):
    print(
        "\n"
        + "=" * 65
    )

    if number is not None:
        print(
            f"EVENT #{number}"
        )

    else:
        print(
            "LIVE EVENT"
        )

    print(
        "=" * 65
    )

    print(
        describe_event(
            event
        )
    )

    print(
        "\nEvent Details"
    )

    print(
        "-------------"
    )

    print(
        "Type:          "
        f"{format_label(event.get('event_type'))}"
    )

    print(
        "Event time:    "
        f"{event.get('timestamp', 'Unknown')}"
    )

    print(
        "Zenith time:   "
        f"{event.get('zenith_received_at', 'Unknown')}"
    )

    print(
        "Origin:        "
        f"{format_label(event.get('origin_service'))}"
    )

    print(
        "Site:          "
        f"{event.get('site', 'Unknown')}"
    )

    print(
        "User:          "
        f"{event.get('username', 'Unknown')}"
    )

    print(
        "Department:    "
        f"{format_label(event.get('department'))}"
    )

    print(
        "Role:          "
        f"{event.get('role') or 'Unknown'}"
    )

    print(
        "Source device: "
        f"{event.get('source_device', 'Unknown')}"
    )

    if event.get(
        "resource"
    ):
        print(
            "Resource:      "
            f"{format_label(event['resource'])}"
        )

    if "authenticated" in event:
        print(
            "Authenticated: "
            f"{event['authenticated']}"
        )

    if "access_granted" in event:
        print(
            "Access granted:"
            f" {event['access_granted']}"
        )

    print(
        "Reason:         "
        f"{event.get('reason', 'No reason recorded')}"
    )

    analysis_error = event.get(
        "zenith_analysis_error"
    )

    if analysis_error:
        print(
            "\nZenith Analysis"
        )

        print(
            "---------------"
        )

        print(
            "Analysis was unavailable."
        )

        print(
            f"Error: {analysis_error}"
        )

        return

    features = event.get(
        "zenith_features"
    )

    assessment = event.get(
        "zenith_assessment"
    )

    if features is None or assessment is None:
        print(
            "\nZenith Analysis"
        )

        print(
            "---------------"
        )

        print(
            "No model analysis is stored "
            "for this event."
        )

        return

    display_feature_evidence(
        features
    )

    display_assessment(
        assessment
    )


def display_all_events():
    events = load_events()

    if not events:
        print("\nNo telemetry events found.")
        return

    print("\nZENITH CENTRAL TELEMETRY")
    print("========================")
    print(f"Total events: {len(events)}")

    for number, event in enumerate(
        events,
        start=1
    ):
        display_event(
            event,
            number
        )


def monitor_live_events():
    print("\nZENITH LIVE TELEMETRY")
    print("=====================")
    print("Monitoring for new events...")
    print("Press Ctrl+C to stop.\n")

    while not CENTRAL_LOG_FILE.exists():
        print(
            "Waiting for Zenith telemetry file..."
        )

        time.sleep(1)

    with CENTRAL_LOG_FILE.open(
        "r",
        encoding="utf-8"
    ) as log_file:

        log_file.seek(0, 2)

        while True:
            line = log_file.readline()

            if not line:
                time.sleep(0.5)
                continue

            line = line.strip()

            if not line:
                continue

            try:
                event = json.loads(line)

                display_event(event)

            except json.JSONDecodeError:
                print(
                    "Warning: Invalid telemetry event received."
                )


def main():
    while True:
        print("\nZENITH TELEMETRY VIEWER")
        print("=======================")
        print("1. View stored telemetry")
        print("2. Monitor live telemetry")
        print("3. Exit")

        choice = input(
            "\nSelect an option: "
        )

        if choice == "1":
            display_all_events()

        elif choice == "2":
            try:
                monitor_live_events()

            except KeyboardInterrupt:
                print(
                    "\nLive monitoring stopped."
                )

        elif choice == "3":
            print(
                "Telemetry viewer closed."
            )

            break

        else:
            print(
                "Invalid option."
            )


if __name__ == "__main__":
    main()