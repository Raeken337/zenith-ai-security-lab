import json
from datetime import datetime
from pathlib import Path


LOG_DIRECTORY = Path("data/logs")
LOGIN_LOG_FILE = LOG_DIRECTORY / "login_events.jsonl"


def ensure_log_directory():
    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)


def log_login_event(
    username,
    source_device,
    authenticated,
    reason,
    department=None,
    groups=None
):
    ensure_log_directory()

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "login_success" if authenticated else "login_failure",
        "username": username,
        "source_device": source_device,
        "authenticated": authenticated,
        "reason": reason,
        "department": department,
        "groups": groups or []
    }

    with LOGIN_LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(event) + "\n")

    print(f"Login event recorded: {event['event_type']}")