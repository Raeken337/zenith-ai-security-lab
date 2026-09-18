from datetime import datetime

from simulation.defensive_state import (
    DefensiveStateStore
)


PROTOCOL_TARGETS = {
    "increase_monitoring":
        "user",

    "open_incident":
        "user",

    "alert_administrator":
        "user",

    "require_step_up_authentication":
        "user",

    "invalidate_active_sessions":
        "user",

    "lock_account":
        "user",

    "isolate_endpoint":
        "endpoint",

    "restrict_lateral_movement":
        "endpoint",

    "protect_target_resource":
        "resource",

    "send_urgent_administrator_alert":
        "user"
}


class ZenithProtocolExecutor:
    def __init__(
        self,
        state_store=None
    ):
        self.state_store = (
            state_store
            or DefensiveStateStore()
        )

    def execute(
        self,
        event,
        decision
    ):
        applied_actions = []
        already_active = []
        skipped_protocols = []
        satisfied_protocols = []

        reason = self._build_reason(
            decision
        )

        for protocol in decision.get(
            "recommended_protocols",
            []
        ):
            if protocol == "record_event":
                satisfied_protocols.append(
                    protocol
                )

                continue

            target_type = (
                PROTOCOL_TARGETS.get(
                    protocol
                )
            )

            if target_type is None:
                skipped_protocols.append({
                    "protocol": protocol,
                    "reason": (
                        "Protocol has no executor "
                        "target mapping."
                    )
                })

                continue

            target = self._resolve_target(
                event,
                target_type
            )

            if not target:
                skipped_protocols.append({
                    "protocol": protocol,
                    "reason": (
                        f"No {target_type} target "
                        "was available."
                    )
                })

                continue

            result = (
                self.state_store.apply_action(
                    protocol=protocol,
                    target_type=target_type,
                    target=target,
                    reason=reason
                )
            )

            if result["created"]:
                applied_actions.append(
                    result["action"]
                )

            else:
                already_active.append(
                    result["action"]
                )

        return {
            "executed_at":
                datetime.now().isoformat(),

            "classification":
                decision.get(
                    "classification"
                ),

            "response_level":
                decision.get(
                    "response_level"
                ),

            "response_name":
                decision.get(
                    "response_name"
                ),

            "applied_actions":
                applied_actions,

            "already_active":
                already_active,

            "satisfied_protocols":
                satisfied_protocols,

            "skipped_protocols":
                skipped_protocols,

            "active_protocols":
                self.state_store
                .active_protocols_for_event(
                    event
                )
        }

    def reverse(
        self,
        action_id
    ):
        return (
            self.state_store
            .reverse_action(
                action_id
            )
        )

    def reset(self):
        self.state_store.reset()

    def _resolve_target(
        self,
        event,
        target_type
    ):
        if target_type == "user":
            return event.get(
                "username"
            )

        if target_type == "endpoint":
            return event.get(
                "source_device"
            )

        if target_type == "resource":
            return event.get(
                "resource"
            )

        if target_type == "global":
            return "zenith"

        return None

    def _build_reason(
        self,
        decision
    ):
        severity = decision.get(
            "incident_severity",
            {}
        )

        return (
            "Zenith response "
            f"level {decision.get('response_level')} "
            f"({decision.get('response_name')}) "
            "for a "
            f"{severity.get('name', 'unknown')} "
            "incident."
        )