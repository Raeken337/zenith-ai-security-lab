import socket
import json
from shared.logger import log_login_event


HOST = "127.0.0.1"
PORT = 5001


USERS = {
    "jake": {
        "password": "Password123",
        "department": "finance",
        "groups": ["employees", "finance"]
    },

    "sarah": {
        "password": "SecurePass456",
        "department": "hr",
        "groups": ["employees", "hr"]
    }
}


def authenticate_user(username, password):
    user = USERS.get(username)

    if user is None:
        return {
            "authenticated": False,
            "reason": "User does not exist"
        }

    if user["password"] != password:
        return {
            "authenticated": False,
            "reason": "Incorrect password"
        }

    return {
        "authenticated": True,
        "reason": "Login successful",
        "department": user["department"],
        "groups": user["groups"]
    }


def start_identity_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Identity Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()

        print(f"\nConnection received from {client_address}")

        raw_message = client_socket.recv(4096).decode("utf-8")

        request = json.loads(raw_message)

        username = request["username"]
        password = request["password"]
        source_device = request["source_device"]

        print(f"Login attempt for user: {username}")
        print(f"Source device: {source_device}")

        response = authenticate_user(
            username,
            password
        )

        log_login_event(
            username=username,
            source_device=source_device,
            authenticated=response["authenticated"],
            reason=response["reason"],
            department=response.get("department"),
            groups=response.get("groups")
        )

        client_socket.send(
            json.dumps(response).encode("utf-8")
        )

        client_socket.close()


if __name__ == "__main__":
    start_identity_server()