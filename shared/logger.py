import json
from datetime import datetime
from pathlib import Path
from shared.telemetry_client import send_event_to_zenith


LOG_DIRECTORY = Path("data/logs")

LOGIN_LOG_FILE = LOG_DIRECTORY / "login_events.jsonl"
FILE_ACCESS_LOG_FILE = LOG_DIRECTORY / "file_access_events.jsonl"
ACCOUNT_LOG_FILE = LOG_DIRECTORY / "account_events.jsonl"


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

    if authenticated:
        event_type = "login_success"

    elif "locked" in reason.lower():
        event_type = "account_locked"

    else:
        event_type = "login_failure"

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "origin_service": "identity_server",
        "site": "SITE_A",
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

    send_event_to_zenith(event)


def log_file_access_event(
    username,
    source_device,
    resource,
    access_granted,
    reason
):
    ensure_log_directory()

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "origin_service": "file_server",
        "site": "SITE_A",
        "username": username,
        "source_device": source_device,
        "resource": resource,
        "access_granted": access_granted,
        "reason": reason
    }

    with FILE_ACCESS_LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(event) + "\n")

    print(f"File access event recorded: {event['event_type']}")
    send_event_to_zenith(event)


def log_account_event(
    username,
    source_device,
    event_type,
    reason
):
    ensure_log_directory()

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "origin_service": "identity_server",
        "site": "SITE_A",
        "username": username,
        "source_device": source_device,
        "reason": reason
    }

    with ACCOUNT_LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(event) + "\n")

    print(f"Account event recorded: {event['event_type']}")
    send_event_to_zenith(event)
