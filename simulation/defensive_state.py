import json

from datetime import datetime
from pathlib import Path
from uuid import uuid4


DEFAULT_STATE_FILE = Path(
    "data/runtime/defensive_state.json"
)


STATE_VERSION = 1


class DefensiveStateStore:
    def __init__(
        self,
        state_file=None
    ):
        self.state_file = Path(
            state_file
            or DEFAULT_STATE_FILE
        )

    def apply_action(
        self,
        protocol,
        target_type,
        target,
        reason
    ):
        state = self._load_state()

        existing_action = (
            self._find_active_action(
                state=state,
                protocol=protocol,
                target_type=target_type,
                target=target
            )
        )

        if existing_action is not None:
            return {
                "created": False,
                "action": existing_action
            }

        action = {
            "action_id":
                uuid4().hex,

            "protocol":
                protocol,

            "target_type":
                target_type,

            "target":
                target,

            "status":
                "active",

            "reason":
                reason,

            "applied_at":
                datetime.now().isoformat(),

            "reversed_at":
                None
        }

        state["actions"].append(
            action
        )

        self._write_state(
            state
        )

        return {
            "created": True,
            "action": action
        }

    def reverse_action(
        self,
        action_id
    ):
        state = self._load_state()

        for action in state["actions"]:
            if action[
                "action_id"
            ] != action_id:
                continue

            if action["status"] == "active":
                action["status"] = "reversed"

                action["reversed_at"] = (
                    datetime.now().isoformat()
                )

                self._write_state(
                    state
                )

            return action

        return None

    def reset(self):
        self._write_state(
            self._empty_state()
        )

    def list_actions(
        self,
        active_only=False
    ):
        actions = self._load_state()[
            "actions"
        ]

        if active_only:
            actions = [
                action
                for action in actions
                if action["status"] == "active"
            ]

        return [
            dict(action)
            for action in actions
        ]

    def active_protocols_for_event(
        self,
        event
    ):
        username = event.get(
            "username"
        )

        source_device = event.get(
            "source_device"
        )

        resource = event.get(
            "resource"
        )

        matching_targets = {
            (
                "user",
                username
            ),
            (
                "endpoint",
                source_device
            ),
            (
                "resource",
                resource
            ),
            (
                "global",
                "zenith"
            )
        }

        protocols = {
            action["protocol"]
            for action in self.list_actions(
                active_only=True
            )
            if (
                action["target_type"],
                action["target"]
            ) in matching_targets
        }

        return sorted(
            protocols
        )

    def is_account_locked(
        self,
        username
    ):
        return self._has_active_protocol(
            protocol="lock_account",
            target_type="user",
            target=username
        )

    def requires_step_up(
        self,
        username
    ):
        return self._has_active_protocol(
            protocol=(
                "require_step_up_authentication"
            ),
            target_type="user",
            target=username
        )

    def session_invalidation_time(
        self,
        username
    ):
        invalidation_actions = [
            action
            for action in self.list_actions()
            if (
                action["protocol"]
                == "invalidate_active_sessions"
                and action["target_type"]
                == "user"
                and action["target"]
                == username
            )
        ]

        if not invalidation_actions:
            return None

        latest_action = max(
            invalidation_actions,
            key=lambda action: (
                action["applied_at"]
            )
        )

        return latest_action[
            "applied_at"
        ]

    def is_endpoint_isolated(
        self,
        source_device
    ):
        return self._has_active_protocol(
            protocol="isolate_endpoint",
            target_type="endpoint",
            target=source_device
        )

    def is_lateral_movement_restricted(
        self,
        source_device
    ):
        return self._has_active_protocol(
            protocol=(
                "restrict_lateral_movement"
            ),
            target_type="endpoint",
            target=source_device
        )

    def is_resource_protected(
        self,
        resource
    ):
        return self._has_active_protocol(
            protocol="protect_target_resource",
            target_type="resource",
            target=resource
        )

    def snapshot(self):
        return self._load_state()

    def _has_active_protocol(
        self,
        protocol,
        target_type,
        target
    ):
        state = self._load_state()

        return (
            self._find_active_action(
                state=state,
                protocol=protocol,
                target_type=target_type,
                target=target
            )
            is not None
        )

    def _find_active_action(
        self,
        state,
        protocol,
        target_type,
        target
    ):
        for action in state["actions"]:
            if (
                action["status"] == "active"
                and action["protocol"]
                == protocol
                and action["target_type"]
                == target_type
                and action["target"]
                == target
            ):
                return action

        return None

    def _load_state(self):
        if not self.state_file.exists():
            return self._empty_state()

        with self.state_file.open(
            "r",
            encoding="utf-8"
        ) as state_file:
            state = json.load(
                state_file
            )

        self._validate_state(
            state
        )

        return state

    def _write_state(
        self,
        state
    ):
        self.state_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temporary_file = (
            self.state_file.with_suffix(
                ".tmp"
            )
        )

        with temporary_file.open(
            "w",
            encoding="utf-8"
        ) as state_file:
            json.dump(
                state,
                state_file,
                indent=2
            )

        temporary_file.replace(
            self.state_file
        )

    def _empty_state(self):
        return {
            "version": STATE_VERSION,
            "actions": []
        }

    def _validate_state(
        self,
        state
    ):
        if state.get(
            "version"
        ) != STATE_VERSION:
            raise ValueError(
                "Unsupported defensive-state "
                "version."
            )

        if not isinstance(
            state.get("actions"),
            list
        ):
            raise ValueError(
                "Defensive state must contain "
                "an actions list."
            )