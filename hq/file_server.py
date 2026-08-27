import socket
import json

from shared.logger import log_file_access_event

from office.finance_team import can_finance_role_access
from office.hr_team import can_hr_role_access
from office.sales_team import can_sales_role_access
from office.it_team import can_it_role_access
from office.office_admin_team import can_office_admin_role_access


HOST = "127.0.0.1"
PORT = 5002

IDENTITY_SERVER_HOST = "127.0.0.1"
IDENTITY_SERVER_PORT = 5001


RESOURCES = {
    # General
    "company_handbook": {
        "content": "General company policies and procedures."
    },

    # Finance
    "finance_payroll": {
        "content": "Sensitive company payroll information."
    },

    "finance_reports": {
        "content": "Internal financial reporting information."
    },

    "finance_invoices": {
        "content": "Company invoice and payment records."
    },

    # HR
    "hr_records": {
        "content": "Restricted HR case and personnel information."
    },

    "employee_records": {
        "content": "Employee profile and employment records."
    },

    "recruitment_files": {
        "content": "Recruitment and candidate documentation."
    },

    "training_records": {
        "content": "Employee learning and training records."
    },

    "absence_records": {
        "content": "Employee absence and attendance records."
    },

    # Sales
    "sales_crm": {
        "content": "Internal customer relationship records."
    },

    "customer_accounts": {
        "content": "Customer account information."
    },

    "sales_reports": {
        "content": "Internal sales performance reports."
    },

    "pricing_documents": {
        "content": "Internal pricing information."
    },

    "product_information": {
        "content": "Internal product and service information."
    },

    # Office Administration
    "office_reports": {
        "content": "Office-level operational reports."
    },

    "site_documents": {
        "content": "Office site administration documents."
    },

    "staff_directory": {
        "content": "Internal employee contact directory."
    },

    # IT / Technical
    "identity_support": {
        "content": "Identity support service interface."
    },

    "account_management": {
        "content": "User account administration interface."
    },

    "password_reset_tools": {
        "content": "Corporate password reset tools."
    },

    "endpoint_management": {
        "content": "Endpoint management interface."
    },

    "remote_admin": {
        "content": "Remote administration service."
    },

    "device_inventory": {
        "content": "Corporate endpoint inventory."
    },

    "network_logs": {
        "content": "Network infrastructure event logs."
    },

    "security_logs": {
        "content": "Security monitoring logs."
    },

    "event_viewer": {
        "content": "System event viewer."
    },

    "telemetry_logs": {
        "content": "Central infrastructure telemetry records."
    },

    "file_server_admin": {
        "content": "File server administration interface."
    },

    "identity_server_admin": {
        "content": "Identity server administration interface."
    },

    "hq_admin_tools": {
        "content": "HQ infrastructure administration tools."
    },

    "hq_system_logs": {
        "content": "HQ system and service logs."
    },

    "hq_remote_services": {
        "content": "HQ remote administration services."
    },

    "zenith_event_viewer": {
        "content": "Zenith security event viewer."
    },

    "zenith_node_status": {
        "content": "Zenith node operational status."
    },

    "zenith_operational_logs": {
        "content": "Zenith operational logging information."
    }
}


def normalize_resource_name(resource):
    return "_".join(
        resource.strip().lower().split()
    )

def validate_session_with_identity_server(session_token):
    identity_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        identity_socket.connect(
            (
                IDENTITY_SERVER_HOST,
                IDENTITY_SERVER_PORT
            )
        )

        request = {
            "action": "validate_session",
            "session_token": session_token
        }

        identity_socket.sendall(
            json.dumps(request).encode("utf-8")
        )

        raw_response = identity_socket.recv(
            4096
        ).decode("utf-8")

        return json.loads(raw_response)

    finally:
        identity_socket.close()


def role_can_access(
    department,
    role,
    resource
):
    if department == "finance":
        return can_finance_role_access(
            role,
            resource
        )

    if department == "hr":
        return can_hr_role_access(
            role,
            resource
        )

    if department == "sales":
        return can_sales_role_access(
            role,
            resource
        )

    if department == "it":
        return can_it_role_access(
            role,
            resource
        )

    if department == "office_admin":
        return can_office_admin_role_access(
            role,
            resource
        )

    return False


def check_resource_access(
    department,
    role,
    resource
):
    if resource not in RESOURCES:
        return (
            False,
            "Resource does not exist"
        )

    access_granted = role_can_access(
        department,
        role,
        resource
    )

    if access_granted:
        return (
            True,
            "Role authorised for resource"
        )

    return (
        False,
        "Role is not authorised for resource"
    )


def handle_file_request(request):
    session_token = request.get(
        "session_token"
    )

    source_device = request.get(
        "source_device",
        "UNKNOWN"
    )

    resource = request.get(
        "resource"
    )

    if resource:
        resource = normalize_resource_name(
            resource
        )

    if not session_token:
        return {
            "access_granted": False,
            "reason": "Session token missing"
        }

    if not resource:
        return {
            "access_granted": False,
            "reason": "Resource not specified"
        }

    session = validate_session_with_identity_server(
        session_token
    )

    if not session["valid"]:
        return {
            "access_granted": False,
            "reason": session["reason"]
        }
    session_device = session.get(
    "source_device"
)

    if session_device != source_device:
        return {
            "access_granted": False,
            "reason": (
                "Session is not valid "
                "for this device"
            )
        }

    username = session["username"]
    full_name = session["full_name"]
    department = session["department"]
    role = session["role"]

    access_granted, reason = check_resource_access(
        department,
        role,
        resource
    )

    log_file_access_event(
        username=username,
        source_device=source_device,
        resource=resource,
        access_granted=access_granted,
        reason=reason,
        department=department,
        role=role
    )

    response = {
        "access_granted": access_granted,
        "reason": reason,
        "username": username,
        "full_name": full_name,
        "department": department,
        "role": role,
        "resource": resource
    }

    if access_granted:
        response["content"] = (
            RESOURCES[resource]["content"]
        )

    return response


def start_file_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen()

    print(
        f"File Server listening "
        f"on {HOST}:{PORT}"
    )

    print(
        f"Available resources: "
        f"{len(RESOURCES)}"
    )

    while True:
        client_socket, client_address = (
            server_socket.accept()
        )

        print(
            f"\nFile request received "
            f"from {client_address}"
        )

        try:
            raw_message = client_socket.recv(
                4096
            ).decode("utf-8")

            request = json.loads(
                raw_message
            )

            response = handle_file_request(
                request
            )

            client_socket.sendall(
                json.dumps(response).encode(
                    "utf-8"
                )
            )

        finally:
            client_socket.close()


if __name__ == "__main__":
    start_file_server()