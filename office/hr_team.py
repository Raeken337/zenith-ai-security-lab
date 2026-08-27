from shared.user import User
from shared.endpoint import Endpoint


HR_USERS = [
    User(
        username="sarah",
        full_name="Sarah Mitchell",
        department="hr",
        groups=["employees", "hr"],
        role="HR Manager",
        work_start=8,
        work_end=17
    ),

    User(
        username="amelia",
        full_name="Amelia Foster",
        department="hr",
        groups=["employees", "hr"],
        role="Senior HR Advisor",
        work_start=8,
        work_end=17
    ),

    User(
        username="ethan",
        full_name="Ethan Ward",
        department="hr",
        groups=["employees", "hr"],
        role="HR Advisor",
        work_start=9,
        work_end=17
    ),

    User(
        username="chloe",
        full_name="Chloe Turner",
        department="hr",
        groups=["employees", "hr"],
        role="HR Advisor",
        work_start=9,
        work_end=17
    ),

    User(
        username="mason",
        full_name="Mason Reed",
        department="hr",
        groups=["employees", "hr"],
        role="Recruitment Coordinator",
        work_start=9,
        work_end=18
    ),

    User(
        username="isla",
        full_name="Isla Cooper",
        department="hr",
        groups=["employees", "hr"],
        role="Recruitment Advisor",
        work_start=8,
        work_end=17
    ),

    User(
        username="leo",
        full_name="Leo Richardson",
        department="hr",
        groups=["employees", "hr"],
        role="Learning and Development Coordinator",
        work_start=9,
        work_end=17
    ),

    User(
        username="ava",
        full_name="Ava Collins",
        department="hr",
        groups=["employees", "hr"],
        role="Employee Relations Advisor",
        work_start=8,
        work_end=17
    ),

    User(
        username="harry",
        full_name="Harry Bennett",
        department="hr",
        groups=["employees", "hr"],
        role="People Operations Administrator",
        work_start=9,
        work_end=17
    ),

    User(
        username="mia",
        full_name="Mia Edwards",
        department="hr",
        groups=["employees", "hr"],
        role="HR Administrator",
        work_start=9,
        work_end=17
    ),

    User(
        username="archie",
        full_name="Archie Foster",
        department="hr",
        groups=["employees", "hr"],
        role="HR Assistant",
        work_start=9,
        work_end=17
    ),

    User(
        username="lily",
        full_name="Lily Hughes",
        department="hr",
        groups=["employees", "hr"],
        role="HR Assistant",
        work_start=9,
        work_end=17
    )
]


HR_ENDPOINTS = [
    Endpoint(
        device_id="LAP-HR-01",
        device_type="laptop",
        assigned_user="sarah",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-HR-02",
        device_type="laptop",
        assigned_user="amelia",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-HR-01",
        device_type="desktop",
        assigned_user="ethan",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-HR-02",
        device_type="desktop",
        assigned_user="chloe",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-HR-03",
        device_type="desktop",
        assigned_user="mason",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="LAP-HR-03",
        device_type="laptop",
        assigned_user="isla",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-HR-04",
        device_type="desktop",
        assigned_user="leo",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="LAP-HR-04",
        device_type="laptop",
        assigned_user="ava",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-HR-05",
        device_type="desktop",
        assigned_user="harry",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-HR-06",
        device_type="desktop",
        assigned_user="mia",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-HR-07",
        device_type="desktop",
        assigned_user="archie",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-HR-08",
        device_type="desktop",
        assigned_user="lily",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="MOB-HR-01",
        device_type="mobile",
        assigned_user="sarah",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-HR-02",
        device_type="mobile",
        assigned_user="ava",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-HR-03",
        device_type="mobile",
        assigned_user="mason",
        site="OFFICE",
        connection_type="wireless"
    )
]


HR_ALLOWED_RESOURCES = [
    "company_handbook",
    "hr_records",
    "employee_records",
    "recruitment_files",
    "training_records",
    "absence_records"
]


def get_hr_users():
    return HR_USERS


def get_hr_endpoints():
    return HR_ENDPOINTS


def get_hr_summary():
    return {
        "department": "hr",
        "user_count": len(HR_USERS),
        "endpoint_count": len(HR_ENDPOINTS),
        "allowed_resources": HR_ALLOWED_RESOURCES
    }


if __name__ == "__main__":
    print("HR DEPARTMENT")
    print("=============")

    summary = get_hr_summary()

    print(f"Users: {summary['user_count']}")
    print(f"Endpoints: {summary['endpoint_count']}")
    print(
        f"Allowed resources: "
        f"{summary['allowed_resources']}"
    )

    print("\nEmployees")
    print("---------")

    for user in HR_USERS:
        print(
            f"{user.full_name} | "
            f"{user.role} | "
            f"{user.username}"
        )

    print("\nEndpoints")
    print("---------")

    for endpoint in HR_ENDPOINTS:
        print(
            f"{endpoint.device_id} | "
            f"{endpoint.device_type} | "
            f"{endpoint.assigned_user} | "
            f"{endpoint.connection_type}"
        )