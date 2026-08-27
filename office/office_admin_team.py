from shared.user import User
from shared.endpoint import Endpoint


OFFICE_ADMIN_USERS = [
    User(
        username="victoria",
        full_name="Victoria Hale",
        department="office_admin",
        groups=["employees", "office_admin"],
        role="Office Manager",
        work_start=8,
        work_end=18
    ),

    User(
        username="ben",
        full_name="Ben Lawson",
        department="office_admin",
        groups=["employees", "office_admin"],
        role="Deputy Office Manager",
        work_start=8,
        work_end=17
    ),

    User(
        username="nina",
        full_name="Nina Shah",
        department="office_admin",
        groups=["employees", "office_admin"],
        role="Site Administrator",
        work_start=9,
        work_end=17
    )
]


OFFICE_ADMIN_ENDPOINTS = [
    Endpoint(
        device_id="LAP-ADM-01",
        device_type="laptop",
        assigned_user="victoria",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-ADM-02",
        device_type="laptop",
        assigned_user="ben",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-ADM-01",
        device_type="desktop",
        assigned_user="nina",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="MOB-ADM-01",
        device_type="mobile",
        assigned_user="victoria",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-ADM-02",
        device_type="mobile",
        assigned_user="ben",
        site="OFFICE",
        connection_type="wireless"
    )
]


OFFICE_ADMIN_ALLOWED_RESOURCES = [
    "company_handbook",

    "finance_reports",
    "finance_invoices",

    "hr_records",
    "employee_records",
    "recruitment_files",
    "training_records",
    "absence_records",

    "sales_crm",
    "customer_accounts",
    "sales_reports",
    "pricing_documents",
    "product_information",

    "office_reports",
    "site_documents",
    "staff_directory"
]


OFFICE_ADMIN_ROLE_ACCESS = {
    "Office Manager": [
        "company_handbook",

        "finance_reports",
        "finance_invoices",

        "hr_records",
        "employee_records",
        "recruitment_files",
        "training_records",
        "absence_records",

        "sales_crm",
        "customer_accounts",
        "sales_reports",
        "pricing_documents",
        "product_information",

        "office_reports",
        "site_documents",
        "staff_directory"
    ],

    "Deputy Office Manager": [
        "company_handbook",

        "finance_reports",
        "finance_invoices",

        "employee_records",
        "recruitment_files",
        "training_records",
        "absence_records",

        "sales_crm",
        "customer_accounts",
        "sales_reports",
        "pricing_documents",
        "product_information",

        "office_reports",
        "site_documents",
        "staff_directory"
    ],

    "Site Administrator": [
        "company_handbook",
        "employee_records",
        "recruitment_files",

        "sales_crm",
        "customer_accounts",

        "office_reports",
        "site_documents",
        "staff_directory"
    ]
}


def get_office_admin_users():
    return OFFICE_ADMIN_USERS


def get_office_admin_endpoints():
    return OFFICE_ADMIN_ENDPOINTS


def get_office_admin_role_access(role):
    return OFFICE_ADMIN_ROLE_ACCESS.get(
        role,
        []
    )


def can_office_admin_role_access(role, resource):
    allowed_resources = get_office_admin_role_access(role)

    return resource in allowed_resources


def get_office_admin_summary():
    return {
        "department": "office_admin",
        "user_count": len(OFFICE_ADMIN_USERS),
        "endpoint_count": len(OFFICE_ADMIN_ENDPOINTS),
        "allowed_resources": OFFICE_ADMIN_ALLOWED_RESOURCES
    }


if __name__ == "__main__":
    print("OFFICE ADMINISTRATION")
    print("=====================")

    summary = get_office_admin_summary()

    print(f"Users: {summary['user_count']}")
    print(f"Endpoints: {summary['endpoint_count']}")
    print(
        f"Allowed resources: "
        f"{summary['allowed_resources']}"
    )

    print("\nEmployees")
    print("---------")

    for user in OFFICE_ADMIN_USERS:
        print(
            f"{user.full_name} | "
            f"{user.role} | "
            f"{user.username}"
        )

    print("\nEndpoints")
    print("---------")

    for endpoint in OFFICE_ADMIN_ENDPOINTS:
        print(
            f"{endpoint.device_id} | "
            f"{endpoint.device_type} | "
            f"{endpoint.assigned_user} | "
            f"{endpoint.connection_type}"
        )

    print("\nRole Access Test")
    print("----------------")

    print(
        "Victoria accessing finance_reports:",
        can_office_admin_role_access(
            "Office Manager",
            "finance_reports"
        )
    )

    print(
        "Victoria accessing hr_records:",
        can_office_admin_role_access(
            "Office Manager",
            "hr_records"
        )
    )

    print(
        "Ben accessing sales_reports:",
        can_office_admin_role_access(
            "Deputy Office Manager",
            "sales_reports"
        )
    )

    print(
        "Nina accessing site_documents:",
        can_office_admin_role_access(
            "Site Administrator",
            "site_documents"
        )
    )

    print(
        "Nina accessing finance_reports:",
        can_office_admin_role_access(
            "Site Administrator",
            "finance_reports"
        )
    )