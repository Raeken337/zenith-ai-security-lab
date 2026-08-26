import socket
import json


ZENITH_CORE_HOST = "127.0.0.1"
ZENITH_CORE_PORT = 5003


def send_event_to_zenith(event):
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client_socket.settimeout(2)

    try:
        client_socket.connect(
            (ZENITH_CORE_HOST, ZENITH_CORE_PORT)
        )

        client_socket.sendall(
            json.dumps(event).encode("utf-8")
        )

        response = client_socket.recv(4096).decode("utf-8")

        return json.loads(response)

    except OSError as error:
        print(f"Zenith telemetry unavailable: {error}")

        return {
            "received": False,
            "reason": "Zenith Core unavailable"
        }

    finally:
        client_socket.close()