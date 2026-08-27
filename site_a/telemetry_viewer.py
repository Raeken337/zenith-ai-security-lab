import json
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


def display_event(event, number):
    print("\n" + "=" * 55)

    print(f"EVENT #{number}")

    print("-" * 55)

    print(
        f"Type:           "
        f"{event.get('event_type', 'Unknown')}"
    )

    print(
        f"Time:           "
        f"{event.get('timestamp', 'Unknown')}"
    )

    print(
        f"Zenith received:"
        f" {event.get('zenith_received_at', 'Unknown')}"
    )

    print(
        f"Origin service: "
        f"{event.get('origin_service', 'Unknown')}"
    )

    print(
        f"Site:           "
        f"{event.get('site', 'Unknown')}"
    )

    print(
        f"User:           "
        f"{event.get('username', 'Unknown')}"
    )

    print(
        f"Source device:  "
        f"{event.get('source_device', 'Unknown')}"
    )

    if "resource" in event:
        print(
            f"Resource:       "
            f"{event['resource']}"
        )

    if "authenticated" in event:
        print(
            f"Authenticated:  "
            f"{event['authenticated']}"
        )

    if "access_granted" in event:
        print(
            f"Access granted: "
            f"{event['access_granted']}"
        )

    print(
        f"Reason:         "
        f"{event.get('reason', 'No reason recorded')}"
    )


def display_all_events():
    events = load_events()

    if not events:
        print("\nNo telemetry events found.")
        return

    print("\nZENITH CENTRAL TELEMETRY")
    print("========================")

    print(
        f"Total events: {len(events)}"
    )

    for number, event in enumerate(
        events,
        start=1
    ):
        display_event(
            event,
            number
        )


if __name__ == "__main__":
    display_all_events()