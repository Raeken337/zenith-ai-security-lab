import random
import pandas as pd

from office.finance_team import get_finance_users
from office.hr_team import get_hr_users
from office.sales_team import get_sales_users
from office.it_team import get_it_users
from office.office_admin_team import get_office_admin_users


def load_users():
    return (
        get_finance_users()
        + get_hr_users()
        + get_sales_users()
        + get_it_users()
        + get_office_admin_users()
    )


USERS = load_users()

RESOURCE_SENSITIVITY = {
    "company_handbook": 1,
    "product_information": 1,
    "staff_directory": 1,

    "finance_reports": 2,
    "finance_invoices": 2,
    "sales_reports": 2,
    "sales_crm": 2,
    "customer_accounts": 2,
    "training_records": 2,

    "finance_payroll": 3,
    "hr_records": 3,
    "employee_records": 3,
    "absence_records": 3,
    "pricing_documents": 3,

    "network_logs": 3,
    "security_logs": 4,
    "telemetry_logs": 4,
    "remote_admin": 4,
    "file_server_admin": 5,
    "identity_server_admin": 5,
    "hq_admin_tools": 5
}

def choose_resource_sensitivity(
    minimum=1,
    maximum=5
):
    return random.randint(
        minimum,
        maximum
    )


def choose_sequence_pattern(label):
    patterns = {
        "normal": [
            "routine_access",
            "normal_login_access",
            "repeated_legitimate_access"
        ],

        "human_error": [
            "failed_login_recovery",
            "password_reset_recovery",
            "single_access_mistake",
            "routine_access"
        ],

        "suspicious": [
            "resource_probe",
            "repeated_denial",
            "unusual_traversal",
            "mixed_access_pattern",
            "routine_access"
        ],

        "malicious": [
            "privilege_probe",
            "resource_traversal",
            "repeated_denial",
            "credential_abuse",
            "low_and_slow_probe",
            "routine_access"
        ]
    }

    return random.choice(
        patterns[label]
    )

NORMAL_EVENTS = [
    "login_success",
    "file_access_success"
]

ERROR_EVENTS = [
    "login_failure",
    "password_reset",
    "file_access_denied"
]

SUSPICIOUS_EVENTS = [
    "file_access_denied",
    "login_failure"
]

MALICIOUS_EVENTS = [
    "file_access_denied",
    "login_failure"
]


def generate_normal_event(user):
    off_hours = random.choices(
        [0, 1],
        weights=[92, 8]
    )[0]

    if off_hours:
        hour = random.choice([
            random.randint(6, 7),
            random.randint(18, 21)
        ])
    else:
        hour = random.randint(
            user.work_start,
            user.work_end
        )

    failed_logins = random.choices(
        [0, 1, 2],
        weights=[88, 10, 2]
    )[0]

    denied_accesses = random.choices(
        [0, 1],
        weights=[95, 5]
    )[0]

    recent_password_reset = random.choices(
        [0, 1],
        weights=[97, 3]
    )[0]

    successful_recovery = (
        1
        if recent_password_reset
        or failed_logins > 0
        else 0
    )

    successful_recovery = random.choices(
        [successful_recovery, 0],
        weights=[85, 15]
    )[0]

    department_resource_mismatch = (
        random.choices(
            [0, 1],
            weights=[98, 2]
        )[0]
    )

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,

        "event_type": random.choice([
            "login_success",
            "file_access_success"
        ]),

        "hour": hour,

        "failed_logins_10m":
            failed_logins,

        "denied_accesses_10m":
            denied_accesses,

        "unique_resources_30m":
            random.randint(1, 5),

        "off_hours":
            off_hours,

        "role_mismatch":
            random.choices(
                [0, 1],
                weights=[97, 3]
            )[0],

        "device_mismatch": 0,

        "recent_password_reset":
            recent_password_reset,

        "successful_recovery":
            successful_recovery,

        "department_resource_mismatch":
            department_resource_mismatch,

        "resource_sensitivity":
            choose_resource_sensitivity(
                1,
                3
            ),

        "recent_endpoints_used":
            random.choices(
                [1, 2],
                weights=[92, 8]
            )[0],

        "time_since_last_event_seconds":
            random.randint(
                30,
                1800
            ),

        "sequence_pattern":
            choose_sequence_pattern(
                "normal"
            ),

        "historical_user_deviation":
            round(
                random.uniform(
                    0.00,
                    0.25
                ),
                3
            ),

        "user_baseline_risk":
            round(
                random.uniform(
                    0.00,
                    0.20
                ),
                3
            ),

        "repeated_resource_accesses":
            random.randint(
                0,
                4
            ),

        "resource_traversal_count":
            random.randint(
                1,
                3
            ),

        "label": "normal"
    }


def generate_human_error_event(user):
    off_hours = random.choices(
        [0, 1],
        weights=[85, 15]
    )[0]

    if off_hours:
        hour = random.choice([
            random.randint(6, 7),
            random.randint(18, 22)
        ])
    else:
        hour = random.randint(
            user.work_start,
            user.work_end
        )

    failed_logins = random.randint(
        0,
        4
    )

    recent_password_reset = (
        random.choices(
            [0, 1],
            weights=[55, 45]
        )[0]
    )

    successful_recovery = (
        random.choices(
            [0, 1],
            weights=[25, 75]
        )[0]
    )

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,

        "event_type": random.choice([
            "login_failure",
            "password_reset",
            "file_access_denied",
            "login_success"
        ]),

        "hour": hour,

        "failed_logins_10m":
            failed_logins,

        "denied_accesses_10m":
            random.randint(0, 2),

        "unique_resources_30m":
            random.randint(1, 5),

        "off_hours":
            off_hours,

        "role_mismatch":
            random.choices(
                [0, 1],
                weights=[65, 35]
            )[0],

        "device_mismatch":
            random.choices(
                [0, 1],
                weights=[95, 5]
            )[0],

        "recent_password_reset":
            recent_password_reset,

        "successful_recovery":
            successful_recovery,

        "department_resource_mismatch":
            random.choices(
                [0, 1],
                weights=[75, 25]
            )[0],

        "resource_sensitivity":
            choose_resource_sensitivity(
                1,
                4
            ),

        "recent_endpoints_used":
            random.choices(
                [1, 2, 3],
                weights=[80, 18, 2]
            )[0],

        "time_since_last_event_seconds":
            random.randint(
                10,
                900
            ),

        "sequence_pattern":
            choose_sequence_pattern(
                "human_error"
            ),

        "historical_user_deviation":
            round(
                random.uniform(
                    0.10,
                    0.55
                ),
                3
            ),

        "user_baseline_risk":
            round(
                random.uniform(
                    0.05,
                    0.30
                ),
                3
            ),

        "repeated_resource_accesses":
            random.randint(
                0,
                5
            ),

        "resource_traversal_count":
            random.randint(
                1,
                4
            ),

        "label": "human_error"
    }

def generate_suspicious_event(user):
    off_hours = random.choices(
        [0, 1],
        weights=[50, 50]
    )[0]

    if off_hours:
        hour = random.choice([
            random.randint(0, 7),
            random.randint(18, 23)
        ])
    else:
        hour = random.randint(
            user.work_start,
            user.work_end
        )

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,

        "event_type": random.choice([
            "login_success",
            "login_failure",
            "file_access_success",
            "file_access_denied"
        ]),

        "hour": hour,

        "failed_logins_10m":
            random.randint(0, 5),

        "denied_accesses_10m":
            random.randint(0, 4),

        "unique_resources_30m":
            random.randint(2, 8),

        "off_hours":
            off_hours,

        "role_mismatch":
            random.choices(
                [0, 1],
                weights=[45, 55]
            )[0],

        "device_mismatch":
            random.choices(
                [0, 1],
                weights=[75, 25]
            )[0],

        "recent_password_reset":
            random.choices(
                [0, 1],
                weights=[80, 20]
            )[0],

        "successful_recovery":
            random.choices(
                [0, 1],
                weights=[70, 30]
            )[0],

        "department_resource_mismatch":
            random.choices(
                [0, 1],
                weights=[45, 55]
            )[0],

        "resource_sensitivity":
            choose_resource_sensitivity(
                2,
                5
            ),

        "recent_endpoints_used":
            random.randint(
                1,
                3
            ),

        "time_since_last_event_seconds":
            random.randint(
                5,
                600
            ),

        "sequence_pattern":
            choose_sequence_pattern(
                "suspicious"
            ),

        "historical_user_deviation":
            round(
                random.uniform(
                    0.30,
                    0.80
                ),
                3
            ),

        "user_baseline_risk":
            round(
                random.uniform(
                    0.15,
                    0.60
                ),
                3
            ),

        "repeated_resource_accesses":
            random.randint(
                1,
                7
            ),

        "resource_traversal_count":
            random.randint(
                2,
                7
            ),

        "label": "suspicious"
    }


def generate_malicious_event(user):
    off_hours = random.choices(
        [0, 1],
        weights=[65, 35]
    )[0]

    if off_hours:
        hour = random.choice([
            random.randint(0, 7),
            random.randint(18, 23)
        ])
    else:
        hour = random.randint(
            user.work_start,
            user.work_end
        )

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,

        "event_type": random.choice([
            "login_success",
            "login_failure",
            "file_access_success",
            "file_access_denied"
        ]),

        "hour": hour,

        "failed_logins_10m":
            random.randint(0, 6),

        "denied_accesses_10m":
            random.randint(0, 6),

        "unique_resources_30m":
            random.randint(2, 10),

        "off_hours":
            off_hours,

        "role_mismatch":
            random.choices(
                [0, 1],
                weights=[35, 65]
            )[0],

        "device_mismatch":
            random.choices(
                [0, 1],
                weights=[60, 40]
            )[0],

        "recent_password_reset":
            random.choices(
                [0, 1],
                weights=[85, 15]
            )[0],

        "successful_recovery":
            random.choices(
                [0, 1],
                weights=[85, 15]
            )[0],

        "department_resource_mismatch":
            random.choices(
                [0, 1],
                weights=[30, 70]
            )[0],

        "resource_sensitivity":
            choose_resource_sensitivity(
                2,
                5
            ),

        "recent_endpoints_used":
            random.randint(
                1,
                4
            ),

        "time_since_last_event_seconds":
            random.randint(
                1,
                500
            ),

        "sequence_pattern":
            choose_sequence_pattern(
                "malicious"
            ),

        "historical_user_deviation":
            round(
                random.uniform(
                    0.40,
                    1.00
                ),
                3
            ),

        "user_baseline_risk":
            round(
                random.uniform(
                    0.20,
                    0.80
                ),
                3
            ),

        "repeated_resource_accesses":
            random.randint(
                1,
                10
            ),

        "resource_traversal_count":
            random.randint(
                2,
                10
            ),

        "label": "malicious"
    }


def generate_dataset(
    normal_count=4000,
    human_error_count=2000,
    suspicious_count=2000,
    malicious_count=2000
):
    rows = []

    for _ in range(normal_count):
        user = random.choice(USERS)

        rows.append(
            generate_normal_event(user)
        )

    for _ in range(human_error_count):
        user = random.choice(USERS)

        rows.append(
            generate_human_error_event(user)
        )

    for _ in range(suspicious_count):
        user = random.choice(USERS)

        rows.append(
            generate_suspicious_event(user)
        )

    for _ in range(malicious_count):
        user = random.choice(USERS)

        rows.append(
            generate_malicious_event(user)
        )

    dataset = pd.DataFrame(rows)

    return dataset


if __name__ == "__main__":
    dataset = generate_dataset()

    output_path = (
        "data/datasets/"
        "zenith_behaviour_dataset.csv"
    )

    dataset.to_csv(
        output_path,
        index=False
    )

    print(
        f"Generated {len(dataset)} rows."
    )

    print(
        f"Saved dataset to: "
        f"{output_path}"
    )

    print("\nLabel Distribution")
    print("------------------")

    print(
        dataset["label"].value_counts()
    )