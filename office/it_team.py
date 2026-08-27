from shared.user import User
from shared.endpoint import Endpoint


IT_USERS = [
    User(
        username="alex",
        full_name="Alex Turner",
        department="it",
        groups=["employees", "it"],
        role="IT Manager",
        work_start=8,
        work_end=18
    ),

    User(
        username="nathan",
        full_name="Nathan Clarke",
        department="it",
        groups=["employees", "it"],
        role="Senior Systems Administrator",
        work_start=8,
        work_end=17
    ),

    User(
        username="zoe",
        full_name="Zoe Bennett",
        department="it",
        groups=["employees", "it"],
        role="Systems Administrator",
        work_start=8,
        work_end=17
    ),

    User(
        username="ryan",
        full_name="Ryan Foster",
        department="it",
        groups=["employees", "it"],
        role="Network Administrator",
        work_start=8,
        work_end=17
    ),

    User(
        username="hannah",
        full_name="Hannah Morris",
        department="it",
        groups=["employees", "it"],
        role="Security Administrator",
        work_start=8,
        work_end=17
    ),

    User(
        username="adam",
        full_name="Adam Hughes",
        department="it",
        groups=["employees", "it"],
        role="Senior IT Support Engineer",
        work_start=8,
        work_end=17
    ),

    User(
        username="megan",
        full_name="Megan Ward",
        department="it",
        groups=["employees", "it"],
        role="IT Support Engineer",
        work_start=9,
        work_end=18
    ),

    User(
        username="callum",
        full_name="Callum Reed",
        department="it",
        groups=["employees", "it"],
        role="IT Support Technician",
        work_start=9,
        work_end=18
    ),

    User(
        username="erin",
        full_name="Erin Collins",
        department="it",
        groups=["employees", "it"],
        role="Identity and Access Administrator",
        work_start=8,
        work_end=17
    ),

    User(
        username="owen",
        full_name="Owen Richardson",
        department="it",
        groups=["employees", "it"],
        role="Endpoint Administrator",
        work_start=8,
        work_end=17
    ),

    User(
        username="lucy",
        full_name="Lucy Edwards",
        department="it",
        groups=["employees", "it"],
        role="Monitoring and Logging Analyst",
        work_start=9,
        work_end=17
    ),

    User(
        username="sam",
        full_name="Sam Cooper",
        department="it",
        groups=["employees", "it"],
        role="Junior IT Support Technician",
        work_start=9,
        work_end=17
    )
]


IT_ENDPOINTS = [
    Endpoint(
        device_id="LAP-IT-01",
        device_type="laptop",
        assigned_user="alex",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-IT-02",
        device_type="laptop",
        assigned_user="nathan",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-IT-03",
        device_type="laptop",
        assigned_user="zoe",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-IT-04",
        device_type="laptop",
        assigned_user="ryan",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-IT-05",
        device_type="laptop",
        assigned_user="hannah",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-IT-06",
        device_type="laptop",
        assigned_user="adam",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-IT-01",
        device_type="desktop",
        assigned_user="megan",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-IT-02",
        device_type="desktop",
        assigned_user="callum",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="LAP-IT-07",
        device_type="laptop",
        assigned_user="erin",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-IT-08",
        device_type="laptop",
        assigned_user="owen",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-IT-03",
        device_type="desktop",
        assigned_user="lucy",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-IT-04",
        device_type="desktop",
        assigned_user="sam",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="MOB-IT-01",
        device_type="mobile",
        assigned_user="alex",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-IT-02",
        device_type="mobile",
        assigned_user="nathan",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-IT-03",
        device_type="mobile",
        assigned_user="hannah",
        site="OFFICE",
        connection_type="wireless"
    )
]


IT_ALLOWED_RESOURCES = [
    "company_handbook",

    "identity_support",
    "account_management",
    "password_reset_tools",

    "endpoint_management",
    "remote_admin",
    "device_inventory",

    "network_logs",
    "security_logs",
    "event_viewer",
    "telemetry_logs",

    "file_server_admin",
    "identity_server_admin",

    "hq_admin_tools",
    "hq_system_logs",
    "hq_remote_services",

    "zenith_event_viewer",
    "zenith_node_status",
    "zenith_operational_logs"
]


def get_it_users():
    return IT_USERS


def get_it_endpoints():
    return IT_ENDPOINTS


def get_it_summary():
    return {
        "department": "it",
        "user_count": len(IT_USERS),
        "endpoint_count": len(IT_ENDPOINTS),
        "allowed_resources": IT_ALLOWED_RESOURCES
    }


if __name__ == "__main__":
    print("IT DEPARTMENT")
    print("=============")

    summary = get_it_summary()

    print(f"Users: {summary['user_count']}")
    print(f"Endpoints: {summary['endpoint_count']}")
    print(
        f"Allowed resources: "
        f"{summary['allowed_resources']}"
    )

    print("\nEmployees")
    print("---------")

    for user in IT_USERS:
        print(
            f"{user.full_name} | "
            f"{user.role} | "
            f"{user.username}"
        )

    print("\nEndpoints")
    print("---------")

    for endpoint in IT_ENDPOINTS:
        print(
            f"{endpoint.device_id} | "
            f"{endpoint.device_type} | "
            f"{endpoint.assigned_user} | "
            f"{endpoint.connection_type}"
        )