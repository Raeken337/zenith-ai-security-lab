import socket
import json

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


IDENTITY_SERVER_HOST = "127.0.0.1"
IDENTITY_SERVER_PORT = 5001

FILE_SERVER_HOST = "127.0.0.1"
FILE_SERVER_PORT = 5002


def load_office_users():
    return (
        get_finance_users()
        + get_hr_users()
        + get_sales_users()
        + get_it_users()
        + get_office_admin_users()
    )


def load_office_endpoints():
    return (
        get_finance_endpoints()
        + get_hr_endpoints()
        + get_sales_endpoints()
        + get_it_endpoints()
        + get_office_admin_endpoints()
    )


OFFICE_USERS = load_office_users()
OFFICE_ENDPOINTS = load_office_endpoints()


USER_DIRECTORY = {
    user.username: user
    for user in OFFICE_USERS
}


ENDPOINT_DIRECTORY = {
    endpoint.device_id: endpoint
    for endpoint in OFFICE_ENDPOINTS
}


def get_user(username):
    return USER_DIRECTORY.get(username)


def get_user_endpoints(username):
    return [
        endpoint
        for endpoint in OFFICE_ENDPOINTS
        if endpoint.assigned_user == username
    ]


def validate_user_device(username, device_id):
    endpoint = ENDPOINT_DIRECTORY.get(device_id)

    if endpoint is None:
        return False

    return endpoint.assigned_user == username


def send_request(host, port, request):
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        client_socket.connect(
            (host, port)
        )

        client_socket.sendall(
            json.dumps(request).encode("utf-8")
        )

        raw_response = client_socket.recv(
            4096
        ).decode("utf-8")

        return json.loads(raw_response)

    finally:
        client_socket.close()


def login(username, password, device_id):
    request = {
        "action": "login",
        "username": username,
        "password": password,
        "source_device": device_id
    }

    return send_request(
        IDENTITY_SERVER_HOST,
        IDENTITY_SERVER_PORT,
        request
    )


def reset_password(
    username,
    new_password,
    device_id
):
    request = {
        "action": "reset_password",
        "username": username,
        "new_password": new_password,
        "source_device": device_id
    }

    return send_request(
        IDENTITY_SERVER_HOST,
        IDENTITY_SERVER_PORT,
        request
    )


def normalize_resource_name(resource):
    return "_".join(
        resource.strip().lower().split()
    )


def access_resource(
    session_token,
    resource,
    device_id
):
    request = {
        "session_token": session_token,
        "resource": resource,
        "source_device": device_id
    }

    return send_request(
        FILE_SERVER_HOST,
        FILE_SERVER_PORT,
        request
    )


def select_user():
    username = input(
        "\nUsername: "
    ).strip().lower()

    user = get_user(username)

    if user is None:
        print("User does not exist.")
        return None

    print(
        f"\nEmployee: {user.full_name}"
    )

    print(
        f"Department: {user.department}"
    )

    print(
        f"Role: {user.role}"
    )

    return user


def select_endpoint(user):
    endpoints = get_user_endpoints(
        user.username
    )

    if not endpoints:
        print(
            "No endpoint assigned to this user."
        )

        return None

    print("\nAssigned Devices")
    print("----------------")

    for number, endpoint in enumerate(
        endpoints,
        start=1
    ):
        print(
            f"{number}. "
            f"{endpoint.device_id} | "
            f"{endpoint.device_type} | "
            f"{endpoint.connection_type}"
        )

    selection = input(
        "\nSelect device: "
    )

    try:
        index = int(selection) - 1

        if index < 0 or index >= len(endpoints):
            raise IndexError

        endpoint = endpoints[index]

    except (ValueError, IndexError):
        print("Invalid device selection.")
        return None

    return endpoint


def endpoint_session(user, endpoint):
    session_token = None

    while True:
        print("\nOFFICE ENDPOINT")
        print("===============")

        print(
            f"User:   {user.full_name}"
        )

        print(
            f"Role:   {user.role}"
        )

        print(
            f"Device: {endpoint.device_id}"
        )

        print(
            f"Link:   {endpoint.connection_type}"
        )

        print("\n1. Login")
        print("2. Access Resource")
        print("3. Reset Password")
        print("4. Change User / Device")
        print("5. Exit")

        choice = input(
            "\nSelect an option: "
        )

        if choice == "1":
            password = input(
                "Password: "
            )

            response = login(
                username=user.username,
                password=password,
                device_id=endpoint.device_id
            )

            print("\nLogin Response")
            print("--------------")

            if response.get("authenticated"):
                print(
                    f"Login successful. "
                    f"Welcome, {response['full_name']}."
                )

            else:
                print(
                    response.get(
                        "reason",
                        "Login failed."
                    )
                )

            if response.get("authenticated"):
                session_token = response[
                    "session_token"
                ]

        elif choice == "2":
            if session_token is None:
                print(
                    "You must login first."
                )

                continue

            resource = input(
                "Resource name: "
            ).strip()

            resource = normalize_resource_name(resource)

            response = access_resource(
                session_token=session_token,
                resource=resource,
                device_id=endpoint.device_id
            )

            print("\nFile Server Response")
            print("--------------------")

            if response.get("access_granted"):
                print(
                    f"Access granted to "
                    f"{resource.replace('_', ' ').title()}."
                )

            else:
                reason = response.get(
                    "reason",
                    "Access denied"
                )

                if reason == "Resource does not exist":
                    print(
                        "This resource does not exist."
                    )

                elif reason == "Role is not authorised for resource":
                    print(
                        "You are not authorised to access this resource."
                    )

                else:
                    print(reason)

        elif choice == "3":
            new_password = input(
                "New password: "
            )

            response = reset_password(
                username=user.username,
                new_password=new_password,
                device_id=endpoint.device_id
            )

            print("\nPassword Reset Response")
            print("-----------------------")

            print(
                response.get(
                    "reason",
                    "Password reset request completed."
                )
            )

            if response.get(
                "reset_successful"
            ):
                session_token = None

        elif choice == "4":
            return True

        elif choice == "5":
            return False

        else:
            print("Invalid option.")


def main():
    print("\nZENITH OFFICE ENVIRONMENT")
    print("=========================")

    print(
        f"Loaded users: "
        f"{len(OFFICE_USERS)}"
    )

    print(
        f"Loaded endpoints: "
        f"{len(OFFICE_ENDPOINTS)}"
    )

    while True:
        user = select_user()

        if user is None:
            continue

        endpoint = select_endpoint(user)

        if endpoint is None:
            continue

        if not validate_user_device(
            user.username,
            endpoint.device_id
        ):
            print(
                "Selected device is not "
                "assigned to this user."
            )

            continue

        change_identity = endpoint_session(
            user,
            endpoint
        )

        if not change_identity:
            print(
                "Office endpoint closed."
            )

            break


if __name__ == "__main__":
    main()