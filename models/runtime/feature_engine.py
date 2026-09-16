from collections import (
    Counter,
    defaultdict,
    deque
)

from datetime import (
    datetime,
    timedelta
)

from models.model_config import (
    SELECTED_FEATURES
)

from office.finance_team import (
    get_finance_endpoints,
    get_finance_users
)

from office.hr_team import (
    get_hr_endpoints,
    get_hr_users
)

from office.it_team import (
    get_it_endpoints,
    get_it_users
)

from office.office_admin_team import (
    get_office_admin_endpoints,
    get_office_admin_users
)

from office.sales_team import (
    get_sales_endpoints,
    get_sales_users
)


AUTHENTICATION_WINDOW_MINUTES = 10

RESOURCE_WINDOW_MINUTES = 30

DEFAULT_TIME_SINCE_EVENT_SECONDS = 1800


MODEL_EVENT_ALIASES = {
    "account_locked": "login_failure",
    "password_reset_denied": "password_reset"
}


FAILED_AUTHENTICATION_EVENTS = {
    "login_failure",
    "account_locked"
}


RESOURCE_SENSITIVITY = {
    "company_handbook": 1,
    "product_information": 1,
    "staff_directory": 1,

    "finance_reports": 2,
    "finance_invoices": 2,
    "recruitment_files": 2,
    "training_records": 2,
    "sales_reports": 2,
    "sales_crm": 2,
    "customer_accounts": 2,
    "office_reports": 2,
    "site_documents": 2,
    "device_inventory": 2,

    "finance_payroll": 3,
    "hr_records": 3,
    "employee_records": 3,
    "absence_records": 3,
    "pricing_documents": 3,
    "identity_support": 3,
    "network_logs": 3,
    "event_viewer": 3,

    "account_management": 4,
    "password_reset_tools": 4,
    "endpoint_management": 4,
    "remote_admin": 4,
    "security_logs": 4,
    "telemetry_logs": 4,
    "hq_system_logs": 4,
    "zenith_event_viewer": 4,
    "zenith_node_status": 4,
    "zenith_operational_logs": 4,

    "file_server_admin": 5,
    "identity_server_admin": 5,
    "hq_admin_tools": 5,
    "hq_remote_services": 5
}


RESOURCE_DEPARTMENTS = {
    "company_handbook": None,
    "staff_directory": None,

    "finance_payroll": "finance",
    "finance_reports": "finance",
    "finance_invoices": "finance",

    "hr_records": "hr",
    "employee_records": "hr",
    "recruitment_files": "hr",
    "training_records": "hr",
    "absence_records": "hr",

    "sales_crm": "sales",
    "customer_accounts": "sales",
    "sales_reports": "sales",
    "pricing_documents": "sales",
    "product_information": "sales",

    "office_reports": "office_admin",
    "site_documents": "office_admin",

    "identity_support": "it",
    "account_management": "it",
    "password_reset_tools": "it",
    "endpoint_management": "it",
    "remote_admin": "it",
    "device_inventory": "it",
    "network_logs": "it",
    "security_logs": "it",
    "event_viewer": "it",
    "telemetry_logs": "it",
    "file_server_admin": "it",
    "identity_server_admin": "it",
    "hq_admin_tools": "it",
    "hq_system_logs": "it",
    "hq_remote_services": "it",
    "zenith_event_viewer": "it",
    "zenith_node_status": "it",
    "zenith_operational_logs": "it"
}


def load_company_users():
    users = (
        get_finance_users()
        + get_hr_users()
        + get_sales_users()
        + get_it_users()
        + get_office_admin_users()
    )

    return {
        user.username: user
        for user in users
    }


def load_company_endpoints():
    endpoints = (
        get_finance_endpoints()
        + get_hr_endpoints()
        + get_sales_endpoints()
        + get_it_endpoints()
        + get_office_admin_endpoints()
    )

    return {
        endpoint.device_id: endpoint
        for endpoint in endpoints
    }


class FeatureEngine:
    def __init__(self):
        self.user_directory = (
            load_company_users()
        )

        self.endpoint_directory = (
            load_company_endpoints()
        )

        self.event_history = defaultdict(
            deque
        )

        self.last_event_time = {}

    def reset(self):
        self.event_history.clear()
        self.last_event_time.clear()

    def reset_user(self, username):
        self.event_history.pop(
            username,
            None
        )

        self.last_event_time.pop(
            username,
            None
        )

    def process_event(self, event):
        self._validate_event(event)

        username = event["username"]

        event_time = self._parse_timestamp(
            event["timestamp"]
        )

        self._validate_event_order(
            username,
            event_time
        )

        history = self.event_history[
            username
        ]

        self._remove_expired_events(
            history,
            event_time
        )

        stored_event = dict(event)

        stored_event["_parsed_timestamp"] = (
            event_time
        )

        history.append(
            stored_event
        )

        features = self._build_features(
            event=event,
            event_time=event_time,
            current_history=list(history)
        )

        self.last_event_time[
            username
        ] = event_time

        self._validate_feature_schema(
            features
        )

        return {
            feature: features[feature]
            for feature in SELECTED_FEATURES
        }

    def _validate_event(self, event):
        required_fields = {
            "timestamp",
            "event_type",
            "username"
        }

        missing_fields = (
            required_fields
            - set(event)
        )

        if missing_fields:
            raise ValueError(
                "Telemetry event is missing: "
                f"{sorted(missing_fields)}"
            )

        if not event["username"]:
            raise ValueError(
                "Telemetry username cannot be empty."
            )

    def _parse_timestamp(self, timestamp):
        if isinstance(
            timestamp,
            datetime
        ):
            return timestamp

        try:
            return datetime.fromisoformat(
                timestamp
            )

        except (
            TypeError,
            ValueError
        ) as error:
            raise ValueError(
                "Telemetry timestamp must use "
                "ISO 8601 format."
            ) from error

    def _validate_event_order(
        self,
        username,
        event_time
    ):
        previous_time = (
            self.last_event_time.get(
                username
            )
        )

        if (
            previous_time is not None
            and event_time < previous_time
        ):
            raise ValueError(
                "Telemetry events must be processed "
                "in chronological order for each user."
            )

    def _remove_expired_events(
        self,
        history,
        event_time
    ):
        cutoff = (
            event_time
            - timedelta(
                minutes=RESOURCE_WINDOW_MINUTES
            )
        )

        while history:
            oldest_time = history[0][
                "_parsed_timestamp"
            ]

            if oldest_time >= cutoff:
                break

            history.popleft()

    def _events_since(
        self,
        events,
        event_time,
        minutes
    ):
        cutoff = (
            event_time
            - timedelta(
                minutes=minutes
            )
        )

        return [
            event
            for event in events
            if event["_parsed_timestamp"]
            >= cutoff
        ]

    def _normalise_event_type(
        self,
        event_type
    ):
        return MODEL_EVENT_ALIASES.get(
            event_type,
            event_type
        )

    def _resolve_user_context(
        self,
        event
    ):
        username = event["username"]

        user = self.user_directory.get(
            username
        )

        if user is None:
            return {
                "department": event.get(
                    "department",
                    "unknown"
                ),

                "role": event.get(
                    "role",
                    "unknown"
                ),

                "work_start": 8,
                "work_end": 17,

                "known_user": False
            }

        return {
            "department": event.get(
                "department"
            ) or user.department,

            "role": event.get(
                "role"
            ) or user.role,

            "work_start": user.work_start,
            "work_end": user.work_end,

            "known_user": True,

            "expected_department":
                user.department,

            "expected_role":
                user.role
        }

    def _calculate_role_mismatch(
        self,
        user_context
    ):
        if not user_context[
            "known_user"
        ]:
            return 1

        department_mismatch = (
            user_context["department"]
            != user_context[
                "expected_department"
            ]
        )

        role_mismatch = (
            user_context["role"]
            != user_context[
                "expected_role"
            ]
        )

        return int(
            department_mismatch
            or role_mismatch
        )

    def _calculate_device_mismatch(
        self,
        username,
        source_device
    ):
        if not source_device:
            return 1

        endpoint = (
            self.endpoint_directory.get(
                source_device
            )
        )

        if endpoint is None:
            return 1

        return int(
            endpoint.assigned_user
            != username
        )

    def _calculate_off_hours(
        self,
        event_time,
        work_start,
        work_end
    ):
        return int(
            event_time.hour < work_start
            or event_time.hour > work_end
        )

    def _calculate_time_since_event(
        self,
        username,
        event_time
    ):
        previous_time = (
            self.last_event_time.get(
                username
            )
        )

        if previous_time is None:
            return (
                DEFAULT_TIME_SINCE_EVENT_SECONDS
            )

        elapsed_seconds = int(
            (
                event_time
                - previous_time
            ).total_seconds()
        )

        return max(
            1,
            min(
                elapsed_seconds,
                DEFAULT_TIME_SINCE_EVENT_SECONDS
            )
        )

    def _calculate_successful_recovery(
        self,
        recent_events
    ):
        recovery_trigger_observed = False

        recovery_trigger_events = (
            FAILED_AUTHENTICATION_EVENTS
            | {"password_reset"}
        )

        for recent_event in recent_events:
            event_type = recent_event[
                "event_type"
            ]

            if (
                event_type
                in recovery_trigger_events
            ):
                recovery_trigger_observed = True

                continue

            if (
                event_type == "login_success"
                and recovery_trigger_observed
            ):
                return 1

        return 0

    def _calculate_resource_features(
        self,
        current_history,
        event
    ):
        resources = [
            history_event["resource"]
            for history_event in current_history
            if history_event.get(
                "resource"
            )
        ]

        resource_counts = Counter(
            resources
        )

        repeated_accesses = sum(
            max(
                count - 1,
                0
            )
            for count
            in resource_counts.values()
        )

        if resources:
            traversal_count = 1

            for previous, current in zip(
                resources,
                resources[1:]
            ):
                if current != previous:
                    traversal_count += 1

        else:
            traversal_count = 0

        current_resource = event.get(
            "resource"
        )

        return {
            "unique_resources":
                len(set(resources)),

            "repeated_accesses":
                repeated_accesses,

            "traversal_count":
                traversal_count,

            "current_resource":
                current_resource,

            "resource_sensitivity":
                RESOURCE_SENSITIVITY.get(
                    current_resource,
                    0
                )
        }

    def _calculate_department_resource_mismatch(
        self,
        department,
        resource
    ):
        resource_department = (
            RESOURCE_DEPARTMENTS.get(
                resource
            )
        )

        if resource_department is None:
            return 0

        return int(
            resource_department
            != department
        )

    def _build_features(
        self,
        event,
        event_time,

        current_history
    ):
        user_context = (
            self._resolve_user_context(
                event
            )
        )


        current_authentication_history = (
            self._events_since(
                current_history,
                event_time,
                AUTHENTICATION_WINDOW_MINUTES
            )
        )

        resource_features = (
            self._calculate_resource_features(
                current_history,
                event
            )
        )

        source_device = event.get(
            "source_device"
        )

        recent_endpoints = {
            history_event.get(
                "source_device"
            )
            for history_event in current_history
            if history_event.get(
                "source_device"
            )
        }

        failed_logins = sum(
            history_event[
                "event_type"
            ] in FAILED_AUTHENTICATION_EVENTS
            for history_event
            in current_authentication_history
        )

        denied_accesses = sum(
            history_event[
                "event_type"
            ] == "file_access_denied"
            for history_event
            in current_authentication_history
        )

        recent_password_reset = int(
            any(
                history_event[
                    "event_type"
                ] == "password_reset"
                for history_event
                in current_authentication_history
            )
        )

        model_event_type = (
            self._normalise_event_type(
                event["event_type"]
            )
        )

        department = user_context[
            "department"
        ]

        current_resource = (
            resource_features[
                "current_resource"
            ]
        )

        return {
            "department":
                department,

            "role":
                user_context["role"],

            "event_type":
                model_event_type,

            "hour":
                event_time.hour,

            "failed_logins_10m":
                failed_logins,

            "denied_accesses_10m":
                denied_accesses,

            "unique_resources_30m":
                resource_features[
                    "unique_resources"
                ],

            "off_hours":
                self._calculate_off_hours(
                    event_time,
                    user_context["work_start"],
                    user_context["work_end"]
                ),

            "role_mismatch":
                self._calculate_role_mismatch(
                    user_context
                ),

            "device_mismatch":
                self._calculate_device_mismatch(
                    event["username"],
                    source_device
                ),

            "recent_password_reset":
                recent_password_reset,

            "successful_recovery":
                self._calculate_successful_recovery(
                    current_authentication_history
                ),

            "department_resource_mismatch":
                self._calculate_department_resource_mismatch(
                    department,
                    current_resource
                ),

            "resource_sensitivity":
                resource_features[
                    "resource_sensitivity"
                ],

            "recent_endpoints_used":
                len(recent_endpoints),

            "time_since_last_event_seconds":
                self._calculate_time_since_event(
                    event["username"],
                    event_time
                ),

            "repeated_resource_accesses":
                resource_features[
                    "repeated_accesses"
                ],

            "resource_traversal_count":
                resource_features[
                    "traversal_count"
                ]
        }

    def _validate_feature_schema(
        self,
        features
    ):
        expected = set(
            SELECTED_FEATURES
        )

        actual = set(
            features
        )

        if actual != expected:
            raise ValueError({
                "missing_features":
                    sorted(
                        expected - actual
                    ),

                "unexpected_features":
                    sorted(
                        actual - expected
                    )
            })