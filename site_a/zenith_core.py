import socket
import json

from datetime import datetime
from pathlib import Path


HOST = "127.0.0.1"
PORT = 5003

CENTRAL_LOG_FILE = Path(
    "data/logs/central_telemetry.jsonl"
)


def ensure_log_directory():
    CENTRAL_LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


def store_event(event):
    ensure_log_directory()

    central_event = {
        **event,
        "zenith_received_at": datetime.now().isoformat()
    }

    with CENTRAL_LOG_FILE.open(
        "a",
        encoding="utf-8"
    ) as log_file:
        log_file.write(
            json.dumps(central_event) + "\n"
        )

    print(
        f"Telemetry stored: {central_event['event_type']}"
    )


def start_zenith_core():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(
        f"Zenith Core listening on {HOST}:{PORT}"
    )

    while True:
        client_socket, client_address = (
            server_socket.accept()
        )

        print(
            f"\nTelemetry connection from {client_address}"
        )

        raw_message = client_socket.recv(
            4096
        ).decode("utf-8")

        event = json.loads(raw_message)

        print(
            f"Event received: {event['event_type']}"
        )

        print(
            f"Source device: "
            f"{event.get('source_device', 'Unknown')}"
        )

        store_event(event)

        response = {
            "received": True,
            "reason": "Telemetry accepted by Zenith Core"
        }

        client_socket.sendall(
            json.dumps(response).encode("utf-8")
        )

        client_socket.close()


if __name__ == "__main__":
    start_zenith_core()