import socket
import json
import secrets

from shared.logger import (
    log_login_event,
    log_account_event
)

from office.finance_team import get_finance_users
from office.hr_team import get_hr_users
from office.sales_team import get_sales_users
from office.it_team import get_it_users
from office.office_admin_team import get_office_admin_users

from office.finance_team import (
    get_finance_users,
    get_finance_endpoints
)

from office.hr_team import (
    get_hr_users,
    get_hr_endpoints
)

from office.sales_team import (
    get_sales_users,
    get_sales_endpoints
)

from office.it_team import (
    get_it_users,
    get_it_endpoints
)

from office.office_admin_team import (
    get_office_admin_users,
    get_office_admin_endpoints
)


HOST = "127.0.0.1"
PORT = 5001

MAX_FAILED_ATTEMPTS = 3


FAILED_ATTEMPTS = {}
LOCKED_ACCOUNTS = set()
SESSIONS = {}


def load_company_users():
    all_users = (
        get_finance_users()
        + get_hr_users()
        + get_sales_users()
        + get_it_users()
        + get_office_admin_users()
    )

    user_directory = {}

    for user in all_users:
        user_directory[user.username] = {
            "full_name": user.full_name,
            "department": user.department,
            "groups": user.groups,
            "role": user.role,
            "work_start": user.work_start,
            "work_end": user.work_end,

            # Lab-only credential.
            # This is intentionally simple for the simulation.
            "password": f"Zenith-{user.username}-2026!"
        }

    return user_directory

def load_company_endpoints():
    return (
        get_finance_endpoints()
        + get_hr_endpoints()
        + get_sales_endpoints()
        + get_it_endpoints()
        + get_office_admin_endpoints()
    )

USERS = load_company_users()

ENDPOINTS = load_company_endpoints()


ENDPOINT_DIRECTORY = {
    endpoint.device_id: endpoint
    for endpoint in ENDPOINTS
}

def validate_endpoint(username, device_id):
    endpoint = ENDPOINT_DIRECTORY.get(
        device_id
    )

    if endpoint is None:
        return {
            "valid": False,
            "reason": "Device is not registered"
        }

    if endpoint.site != "OFFICE":
        return {
            "valid": False,
            "reason": "Device is not an Office endpoint"
        }

    if endpoint.assigned_user != username:
        return {
            "valid": False,
            "reason": (
                "Device is not assigned "
                "to this user"
            )
        }

    return {
        "valid": True,
        "reason": "Endpoint validated",
        "device_id": endpoint.device_id,
        "device_type": endpoint.device_type,
        "connection_type": endpoint.connection_type,
        "site": endpoint.site
    }

def authenticate_user(
    username,
    password,
    source_device
):
    user = USERS.get(username)

    if user is None:
        return {
            "authenticated": False,
            "reason": "User does not exist"
        }

    if username in LOCKED_ACCOUNTS:
        return {
            "authenticated": False,
            "reason": "Account locked"
        }

    if user["password"] != password:
        FAILED_ATTEMPTS[username] = (
            FAILED_ATTEMPTS.get(username, 0) + 1
        )

        attempts = FAILED_ATTEMPTS[username]

        if attempts >= MAX_FAILED_ATTEMPTS:
            LOCKED_ACCOUNTS.add(username)

            return {
                "authenticated": False,
                "reason": (
                    "Account locked after repeated "
                    "failed login attempts"
                )
            }

        remaining_attempts = (
            MAX_FAILED_ATTEMPTS - attempts
        )

        return {
            "authenticated": False,
            "reason": (
                f"Incorrect password. "
                f"{remaining_attempts} attempts remaining"
            )
        }

    FAILED_ATTEMPTS[username] = 0

    session_token = secrets.token_hex(16)

    SESSIONS[session_token] = {
        "username": username,
        "full_name": user["full_name"],
        "department": user["department"],
        "groups": user["groups"],
        "role": user["role"],
        "work_start": user["work_start"],
        "work_end": user["work_end"],
        "source_device": source_device
    }

    return {
        "authenticated": True,
        "reason": "Login successful",
        "session_token": session_token,
        "username": username,
        "full_name": user["full_name"],
        "department": user["department"],
        "groups": user["groups"],
        "role": user["role"],
        "work_start": user["work_start"],
        "work_end": user["work_end"]
    }


def validate_session(session_token):
    session = SESSIONS.get(session_token)
    

    if session is None:
        return {
            "valid": False,
            "reason": "Invalid session token"
        }

    return {
        "valid": True,
        "reason": "Session validated",
        "username": session["username"],
        "full_name": session["full_name"],
        "department": session["department"],
        "groups": session["groups"],
        "role": session["role"],
        "work_start": session["work_start"],
        "work_end": session["work_end"],
        "source_device": session["source_device"]
    }


def reset_password(
    username,
    new_password,
    source_device
):
    user = USERS.get(username)

    if user is None:
        return {
            "reset_successful": False,
            "reason": "User does not exist"
        }

    if len(new_password) < 8:
        return {
            "reset_successful": False,
            "reason": (
                "Password must contain "
                "at least 8 characters"
            )
        }

    user["password"] = new_password

    FAILED_ATTEMPTS[username] = 0

    LOCKED_ACCOUNTS.discard(username)

    log_account_event(
        username=username,
        source_device=source_device,
        event_type="password_reset",
        reason="Password reset and account unlocked"
    )

    return {
        "reset_successful": True,
        "reason": (
            "Password reset successful. "
            "Account unlocked."
        )
    }


def handle_request(request):
    action = request.get("action")

    if action == "login":
        username = request["username"]
        password = request["password"]
        source_device = request["source_device"]

        print(
            f"\nLogin attempt for user: "
            f"{username}"
        )

        print(
            f"Source device: "
            f"{source_device}"
        )

        endpoint_validation = validate_endpoint(
            username,
            source_device
        )

        if not endpoint_validation["valid"]:
            user = USERS.get(username)

            log_login_event(
                username=username,
                source_device=source_device,
                authenticated=False,
                reason=endpoint_validation["reason"],
                department=(
                    user["department"]
                    if user
                    else None
                ),
                groups=(
                    user["groups"]
                    if user
                    else None
                ),
                role=(
                    user["role"]
                    if user
                    else None
                )
            )

            return {
                "authenticated": False,
                "reason": endpoint_validation["reason"]
            }

        response = authenticate_user(
            username,
            password,
            source_device
        )

        user = USERS.get(username)

        log_login_event(
            username=username,
            source_device=source_device,
            authenticated=response["authenticated"],
            reason=response["reason"],
            department=(
                user["department"]
                if user
                else None
            ),
            groups=(
                user["groups"]
                if user
                else None
            ),
            role=(
                user["role"]
                if user
                else None
            )
        )

        return response

    if action == "validate_session":
        session_token = request["session_token"]

        return validate_session(
            session_token
        )

    if action == "reset_password":
        username = request["username"]
        new_password = request["new_password"]
        source_device = request["source_device"]

        return reset_password(
            username,
            new_password,
            source_device
        )

    if action == "directory_summary":
        return {
            "user_count": len(USERS),
            "departments": {
                "finance": len(
                    get_finance_users()
                ),
                "hr": len(
                    get_hr_users()
                ),
                "sales": len(
                    get_sales_users()
                ),
                "it": len(
                    get_it_users()
                ),
                "office_admin": len(
                    get_office_admin_users()
                )
            }
        }

    return {
        "error": True,
        "reason": "Unknown request action"
    }


def start_identity_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen()

    print(
        f"Identity Server listening "
        f"on {HOST}:{PORT}"
    )

    print(
        f"Loaded users: {len(USERS)}"
    )

    while True:
        client_socket, client_address = (
            server_socket.accept()
        )

        print(
            f"\nConnection received "
            f"from {client_address}"
        )

        raw_message = client_socket.recv(
            4096
        ).decode("utf-8")

        request = json.loads(
            raw_message
        )

        response = handle_request(
            request
        )

        client_socket.sendall(
            json.dumps(response).encode(
                "utf-8"
            )
        )

        client_socket.close()


if __name__ == "__main__":
    start_identity_server()