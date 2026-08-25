import socket
import json


HOST = "127.0.0.1"
PORT = 5001


def login(username, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((HOST, PORT))

    request = {
        "username": username,
        "password": password,
        "source_device": "PC-B1"
    }

    client_socket.send(
        json.dumps(request).encode("utf-8")
    )

    raw_response = client_socket.recv(4096).decode("utf-8")

    response = json.loads(raw_response)

    print("\nIdentity Server Response")
    print("------------------------")
    print(f"Authenticated: {response['authenticated']}")
    print(f"Reason: {response['reason']}")

    if response["authenticated"]:
        print(f"Department: {response['department']}")
        print(f"Groups: {response['groups']}")

    client_socket.close()


if __name__ == "__main__":
    login(
        username="jake",
        password="Password123"
    )