from shared.user import User
from shared.endpoint import Endpoint


SALES_USERS = [
    User(
        username="lucas",
        full_name="Lucas Wright",
        department="sales",
        groups=["employees", "sales"],
        role="Sales Manager",
        work_start=8,
        work_end=18
    ),

    User(
        username="ella",
        full_name="Ella Morris",
        department="sales",
        groups=["employees", "sales"],
        role="Senior Sales Executive",
        work_start=8,
        work_end=17
    ),

    User(
        username="jack",
        full_name="Jack Foster",
        department="sales",
        groups=["employees", "sales"],
        role="Senior Sales Executive",
        work_start=9,
        work_end=18
    ),

    User(
        username="ruby",
        full_name="Ruby Collins",
        department="sales",
        groups=["employees", "sales"],
        role="Sales Executive",
        work_start=9,
        work_end=18
    ),

    User(
        username="alfie",
        full_name="Alfie Turner",
        department="sales",
        groups=["employees", "sales"],
        role="Sales Executive",
        work_start=9,
        work_end=18
    ),

    User(
        username="freya",
        full_name="Freya Bennett",
        department="sales",
        groups=["employees", "sales"],
        role="Sales Executive",
        work_start=9,
        work_end=17
    ),

    User(
        username="oscar",
        full_name="Oscar Reed",
        department="sales",
        groups=["employees", "sales"],
        role="Sales Executive",
        work_start=8,
        work_end=17
    ),

    User(
        username="millie",
        full_name="Millie Hughes",
        department="sales",
        groups=["employees", "sales"],
        role="Account Executive",
        work_start=9,
        work_end=17
    ),

    User(
        username="henry",
        full_name="Henry Cooper",
        department="sales",
        groups=["employees", "sales"],
        role="Account Executive",
        work_start=8,
        work_end=17
    ),

    User(
        username="daisy",
        full_name="Daisy Ward",
        department="sales",
        groups=["employees", "sales"],
        role="Business Development Executive",
        work_start=9,
        work_end=18
    ),

    User(
        username="george",
        full_name="George Richardson",
        department="sales",
        groups=["employees", "sales"],
        role="Business Development Executive",
        work_start=9,
        work_end=18
    ),

    User(
        username="rosie",
        full_name="Rosie Edwards",
        department="sales",
        groups=["employees", "sales"],
        role="Sales Support Coordinator",
        work_start=9,
        work_end=17
    ),

    User(
        username="charlie",
        full_name="Charlie Evans",
        department="sales",
        groups=["employees", "sales"],
        role="Sales Support Assistant",
        work_start=9,
        work_end=17
    ),

    User(
        username="poppy",
        full_name="Poppy Clarke",
        department="sales",
        groups=["employees", "sales"],
        role="Sales Administrator",
        work_start=9,
        work_end=17
    ),

    User(
        username="theo",
        full_name="Theo Martin",
        department="sales",
        groups=["employees", "sales"],
        role="Junior Sales Executive",
        work_start=9,
        work_end=17
    )
]


SALES_ENDPOINTS = [
    Endpoint(
        device_id="LAP-SAL-01",
        device_type="laptop",
        assigned_user="lucas",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-SAL-02",
        device_type="laptop",
        assigned_user="ella",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-SAL-03",
        device_type="laptop",
        assigned_user="jack",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-SAL-01",
        device_type="desktop",
        assigned_user="ruby",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-SAL-02",
        device_type="desktop",
        assigned_user="alfie",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-SAL-03",
        device_type="desktop",
        assigned_user="freya",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-SAL-04",
        device_type="desktop",
        assigned_user="oscar",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="LAP-SAL-04",
        device_type="laptop",
        assigned_user="millie",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-SAL-05",
        device_type="laptop",
        assigned_user="henry",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-SAL-06",
        device_type="laptop",
        assigned_user="daisy",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="LAP-SAL-07",
        device_type="laptop",
        assigned_user="george",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="PC-SAL-05",
        device_type="desktop",
        assigned_user="rosie",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-SAL-06",
        device_type="desktop",
        assigned_user="charlie",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-SAL-07",
        device_type="desktop",
        assigned_user="poppy",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="PC-SAL-08",
        device_type="desktop",
        assigned_user="theo",
        site="OFFICE",
        connection_type="wired"
    ),

    Endpoint(
        device_id="MOB-SAL-01",
        device_type="mobile",
        assigned_user="lucas",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-SAL-02",
        device_type="mobile",
        assigned_user="ella",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-SAL-03",
        device_type="mobile",
        assigned_user="daisy",
        site="OFFICE",
        connection_type="wireless"
    ),

    Endpoint(
        device_id="MOB-SAL-04",
        device_type="mobile",
        assigned_user="george",
        site="OFFICE",
        connection_type="wireless"
    )
]


SALES_ALLOWED_RESOURCES = [
    "company_handbook",
    "sales_crm",
    "customer_accounts",
    "sales_reports",
    "pricing_documents",
    "product_information"
]


def get_sales_users():
    return SALES_USERS


def get_sales_endpoints():
    return SALES_ENDPOINTS


def get_sales_summary():
    return {
        "department": "sales",
        "user_count": len(SALES_USERS),
        "endpoint_count": len(SALES_ENDPOINTS),
        "allowed_resources": SALES_ALLOWED_RESOURCES
    }


if __name__ == "__main__":
    print("SALES DEPARTMENT")
    print("================")

    summary = get_sales_summary()

    print(f"Users: {summary['user_count']}")
    print(f"Endpoints: {summary['endpoint_count']}")
    print(
        f"Allowed resources: "
        f"{summary['allowed_resources']}"
    )

    print("\nEmployees")
    print("---------")

    for user in SALES_USERS:
        print(
            f"{user.full_name} | "
            f"{user.role} | "
            f"{user.username}"
        )

    print("\nEndpoints")
    print("---------")

    for endpoint in SALES_ENDPOINTS:
        print(
            f"{endpoint.device_id} | "
            f"{endpoint.device_type} | "
            f"{endpoint.assigned_user} | "
            f"{endpoint.connection_type}"
        )