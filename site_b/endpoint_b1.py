import socket
import json


IDENTITY_SERVER_HOST = "127.0.0.1"
IDENTITY_SERVER_PORT = 5001

FILE_SERVER_HOST = "127.0.0.1"
FILE_SERVER_PORT = 5002

SOURCE_DEVICE = "PC-B1"


def login(username, password):
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client_socket.connect(
        (IDENTITY_SERVER_HOST, IDENTITY_SERVER_PORT)
    )

    request = {
        "action": "login",
        "username": username,
        "password": password,
        "source_device": SOURCE_DEVICE
    }

    client_socket.send(
        json.dumps(request).encode("utf-8")
    )

    raw_response = client_socket.recv(4096).decode("utf-8")

    client_socket.close()

    return json.loads(raw_response)


def access_file(session_token, resource):
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client_socket.connect(
        (FILE_SERVER_HOST, FILE_SERVER_PORT)
    )

    request = {
        "session_token": session_token,
        "source_device": SOURCE_DEVICE,
        "resource": resource
    }

    client_socket.send(
        json.dumps(request).encode("utf-8")
    )

    raw_response = client_socket.recv(4096).decode("utf-8")

    client_socket.close()

    return json.loads(raw_response)


if __name__ == "__main__":
    login_response = login(
        username="jake",
        password="Password123"
    )

    print("\nLogin Response")
    print("--------------")
    print(login_response)

    if login_response["authenticated"]:
        file_response = access_file(
            session_token=login_response["session_token"],
            resource="finance_payroll"
        )

        print("\nFile Server Response")
        print("--------------------")
        print(file_response)