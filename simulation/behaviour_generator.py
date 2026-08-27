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
    hour = random.randint(
        user.work_start,
        user.work_end
    )

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,
        "event_type": random.choice(
            NORMAL_EVENTS
        ),
        "hour": hour,
        "failed_logins_10m": 0,
        "denied_accesses_10m": 0,
        "unique_resources_30m": random.randint(
            1,
            3
        ),
        "off_hours": 0,
        "role_mismatch": 0,
        "device_mismatch": 0,
        "label": "normal"
    }


def generate_human_error_event(user):
    hour = random.randint(
        user.work_start,
        user.work_end
    )

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,
        "event_type": random.choice(
            ERROR_EVENTS
        ),
        "hour": hour,
        "failed_logins_10m": random.randint(
            1,
            2
        ),
        "denied_accesses_10m": random.randint(
            0,
            1
        ),
        "unique_resources_30m": random.randint(
            1,
            3
        ),
        "off_hours": 0,
        "role_mismatch": random.randint(
            0,
            1
        ),
        "device_mismatch": 0,
        "label": "human_error"
    }


def generate_suspicious_event(user):
    hour = random.choice([
        random.randint(0, 6),
        random.randint(19, 23)
    ])

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,
        "event_type": random.choice(
            SUSPICIOUS_EVENTS
        ),
        "hour": hour,
        "failed_logins_10m": random.randint(
            1,
            4
        ),
        "denied_accesses_10m": random.randint(
            1,
            3
        ),
        "unique_resources_30m": random.randint(
            3,
            6
        ),
        "off_hours": 1,
        "role_mismatch": random.randint(
            0,
            1
        ),
        "device_mismatch": random.randint(
            0,
            1
        ),
        "label": "suspicious"
    }


def generate_malicious_event(user):
    hour = random.choice([
        random.randint(0, 5),
        random.randint(20, 23)
    ])

    return {
        "username": user.username,
        "department": user.department,
        "role": user.role,
        "event_type": random.choice(
            MALICIOUS_EVENTS
        ),
        "hour": hour,
        "failed_logins_10m": random.randint(
            3,
            8
        ),
        "denied_accesses_10m": random.randint(
            3,
            8
        ),
        "unique_resources_30m": random.randint(
            5,
            12
        ),
        "off_hours": 1,
        "role_mismatch": 1,
        "device_mismatch": random.randint(
            0,
            1
        ),
        "label": "malicious"
    }


def generate_dataset(
    normal_count=1000,
    human_error_count=500,
    suspicious_count=500,
    malicious_count=500
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