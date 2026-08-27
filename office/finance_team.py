from shared.user import User
from shared.endpoint import Endpoint


FINANCE_USERS = [
    User(
        username="jake",
        full_name="Jake Morgan",
        department="finance",
        groups=["employees", "finance"],
        role="Financial Analyst",
        work_start=8,
        work_end=17
    ),

    User(
        username="emma",
        full_name="Emma Clarke",
        department="finance",
        groups=["employees", "finance"],
        role="Accounts Payable Assistant",
        work_start=9,
        work_end=17
    ),

    User(
        username="daniel",
        full_name="Daniel Brooks",
        department="finance",
        groups=["employees", "finance"],
        role="Senior Accountant",
        work_start=8,
        work_end=16
    ),

    User(
        username="sophie",
        full_name="Sophie Bennett",
        department="finance",
        groups=["employees", "finance"],
        role="Payroll Administrator",
        work_start=9,
        work_end=17
    ),

    User(
        username="liam",
        full_name="Liam Carter",
        department="finance",
        groups=["employees", "finance"],
        role="Finance Assistant",
        work_start=9,
        work_end=18
    ),

    User(
        username="olivia",
        full_name="Olivia Hughes",
        department="finance",
        groups=["employees", "finance"],
        role="Financial Reporting Accountant",
        work_start=8,
        work_end=17
    ),

    User(
        username="noah",
        full_name="Noah Patel",
        department="finance",
        groups=["employees", "finance"],
        role="Credit Controller",
        work_start=8,
        work_end=16
    ),

    User(
        username="grace",
        full_name="Grace Wilson",
        department="finance",
        groups=["employees", "finance"],
        role="Finance Manager",
        work_start=8,
        work_end=18
    )
]


FINANCE_ENDPOINTS = [
    Endpoint(
        device_id="PC-FIN-01",
        device_type="desktop",
        assigned_user="jake",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-FIN-02",
        device_type="desktop",
        assigned_user="emma",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="LAP-FIN-01",
        device_type="laptop",
        assigned_user="daniel",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-FIN-03",
        device_type="desktop",
        assigned_user="sophie",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-FIN-04",
        device_type="desktop",
        assigned_user="liam",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="LAP-FIN-02",
        device_type="laptop",
        assigned_user="olivia",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-FIN-05",
        device_type="desktop",
        assigned_user="noah",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="LAP-FIN-03",
        device_type="laptop",
        assigned_user="grace",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-FIN-01",
        device_type="mobile",
        assigned_user="olivia",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-FIN-02",
        device_type="mobile",
        assigned_user="grace",
        site="OFFICE",
        connection_type="wireless"
    )
]


FINANCE_ALLOWED_RESOURCES = [
    "company_handbook",
    "finance_payroll",
    "finance_reports",
    "finance_invoices"
]

FINANCE_ROLE_ACCESS = {
    "Finance Manager": [
        "company_handbook",
        "finance_payroll",
        "finance_reports",
        "finance_invoices"
    ],

    "Senior Accountant": [
        "company_handbook",
        "finance_reports",
        "finance_invoices"
    ],

    "Financial Reporting Accountant": [
        "company_handbook",
        "finance_reports",
        "finance_invoices"
    ],

    "Financial Analyst": [
        "company_handbook",
        "finance_reports"
    ],

    "Payroll Administrator": [
        "company_handbook",
        "finance_payroll"
    ],

    "Credit Controller": [
        "company_handbook",
        "finance_reports",
        "finance_invoices"
    ],

    "Accounts Payable Assistant": [
        "company_handbook",
        "finance_invoices"
    ],

    "Finance Assistant": [
        "company_handbook",
        "finance_invoices"
    ]
}

def get_finance_role_access(role):
    return FINANCE_ROLE_ACCESS.get(
        role,
        []
    )

def can_finance_role_access(role, resource):
    allowed_resources = get_finance_role_access(role)

    return resource in allowed_resources
def get_finance_users():
    return FINANCE_USERS


def get_finance_endpoints():
    return FINANCE_ENDPOINTS


def get_finance_summary():
    return {
        "department": "finance",
        "user_count": len(FINANCE_USERS),
        "endpoint_count": len(FINANCE_ENDPOINTS),
        "allowed_resources": FINANCE_ALLOWED_RESOURCES
    }


if __name__ == "__main__":
    print("FINANCE DEPARTMENT")
    print("==================")

    summary = get_finance_summary()

    print(f"Users: {summary['user_count']}")
    print(f"Endpoints: {summary['endpoint_count']}")
    print(
        f"Allowed resources: "
        f"{summary['allowed_resources']}"
    )

    print("\nEmployees")
    print("---------")

    for user in FINANCE_USERS:
        print(
            f"{user.full_name} | "
            f"{user.role} | "
            f"{user.username}"
        )

    print("\nEndpoints")
    print("---------")

    for endpoint in FINANCE_ENDPOINTS:
        print(
            f"{endpoint.device_id} | "
            f"{endpoint.device_type} | "
            f"{endpoint.assigned_user} | "
            f"{endpoint.connection_type}"
        )

    print("\nRole Access Test")
    print("----------------")

    print(
        "Jake accessing finance_reports:",
        can_finance_role_access(
            "Financial Analyst",
            "finance_reports"
        )
    )

    print(
        "Jake accessing finance_payroll:",
        can_finance_role_access(
            "Financial Analyst",
            "finance_payroll"
        )
    )

    print(
        "Grace accessing finance_payroll:",
        can_finance_role_access(
            "Finance Manager",
            "finance_payroll"
        )
    )        