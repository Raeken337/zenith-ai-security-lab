import socket
import json

from shared.logger import log_file_access_event


HOST = "127.0.0.1"
PORT = 5002

IDENTITY_SERVER_HOST = "127.0.0.1"
IDENTITY_SERVER_PORT = 5001


RESOURCES = {
    "company_handbook": {
        "allowed_groups": ["employees"],
        "content": "General company policies and procedures."
    },

    "finance_payroll": {
        "allowed_groups": ["finance"],
        "content": "Sensitive payroll information."
    },

    "hr_records": {
        "allowed_groups": ["hr"],
        "content": "Sensitive employee HR records."
    }
}


def validate_session_with_identity_server(session_token):
    identity_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    identity_socket.connect(
        (IDENTITY_SERVER_HOST, IDENTITY_SERVER_PORT)
    )

    request = {
        "action": "validate_session",
        "session_token": session_token
    }

    identity_socket.send(
        json.dumps(request).encode("utf-8")
    )

    raw_response = identity_socket.recv(4096).decode("utf-8")

    identity_socket.close()

    return json.loads(raw_response)


def check_resource_access(groups, resource):
    resource_info = RESOURCES.get(resource)

    if resource_info is None:
        return False, "Resource does not exist"

    allowed_groups = resource_info["allowed_groups"]

    for group in groups:
        if group in allowed_groups:
            return True, "Access granted"

    return False, "User does not have required permissions"


def handle_file_request(request):
    session_token = request["session_token"]
    source_device = request["source_device"]
    resource = request["resource"]

    session = validate_session_with_identity_server(
        session_token
    )

    if not session["valid"]:
        return {
            "access_granted": False,
            "reason": session["reason"]
        }

    username = session["username"]
    groups = session["groups"]

    access_granted, reason = check_resource_access(
        groups,
        resource
    )

    log_file_access_event(
        username=username,
        source_device=source_device,
        resource=resource,
        access_granted=access_granted,
        reason=reason
    )

    response = {
        "access_granted": access_granted,
        "reason": reason,
        "resource": resource
    }

    if access_granted:
        response["content"] = RESOURCES[resource]["content"]

    return response


def start_file_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"File Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()

        print(f"\nFile request received from {client_address}")

        raw_message = client_socket.recv(4096).decode("utf-8")

        request = json.loads(raw_message)

        response = handle_file_request(request)

        client_socket.send(
            json.dumps(response).encode("utf-8")
        )

        client_socket.close()


if __name__ == "__main__":
    start_file_server()