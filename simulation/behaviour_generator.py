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

    role_mismatch = random.choices(
        [0, 1],
        weights=[97, 3]
    )[0]

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,
        "event_type": random.choice([
            "login_success",
            "file_access_success"
        ]),
        "hour": hour,
        "failed_logins_10m": failed_logins,
        "denied_accesses_10m": denied_accesses,
        "unique_resources_30m": random.randint(
            1,
            5
        ),
        "off_hours": off_hours,
        "role_mismatch": role_mismatch,
        "device_mismatch": 0,
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

    denied_accesses = random.randint(
        0,
        2
    )

    role_mismatch = random.choices(
        [0, 1],
        weights=[65, 35]
    )[0]

    device_mismatch = random.choices(
        [0, 1],
        weights=[95, 5]
    )[0]

    event_type = random.choice([
        "login_failure",
        "password_reset",
        "file_access_denied",
        "login_success"
    ])

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,
        "event_type": event_type,
        "hour": hour,
        "failed_logins_10m": failed_logins,
        "denied_accesses_10m": denied_accesses,
        "unique_resources_30m": random.randint(
            1,
            5
        ),
        "off_hours": off_hours,
        "role_mismatch": role_mismatch,
        "device_mismatch": device_mismatch,
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

    failed_logins = random.randint(
        0,
        5
    )

    denied_accesses = random.randint(
        0,
        4
    )

    role_mismatch = random.choices(
        [0, 1],
        weights=[45, 55]
    )[0]

    device_mismatch = random.choices(
        [0, 1],
        weights=[75, 25]
    )[0]

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
        "failed_logins_10m": failed_logins,
        "denied_accesses_10m": denied_accesses,
        "unique_resources_30m": random.randint(
            2,
            8
        ),
        "off_hours": off_hours,
        "role_mismatch": role_mismatch,
        "device_mismatch": device_mismatch,
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

    failed_logins = random.randint(
        0,
        6
    )

    denied_accesses = random.randint(
        0,
        6
    )

    role_mismatch = random.choices(
        [0, 1],
        weights=[35, 65]
    )[0]

    device_mismatch = random.choices(
        [0, 1],
        weights=[60, 40]
    )[0]

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
        "failed_logins_10m": failed_logins,
        "denied_accesses_10m": denied_accesses,
        "unique_resources_30m": random.randint(
            2,
            10
        ),
        "off_hours": off_hours,
        "role_mismatch": role_mismatch,
        "device_mismatch": device_mismatch,
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