import tempfile
import unittest

from pathlib import Path

from simulation.defensive_state import (
    DefensiveStateStore
)

from simulation.protocol_executor import (
    ZenithProtocolExecutor
)


class ProtocolExecutorTests(
    unittest.TestCase
):
    def setUp(self):
        self.temporary_directory = (
            tempfile.TemporaryDirectory()
        )

        state_file = (
            Path(
                self.temporary_directory.name
            )
            / "defensive_state.json"
        )

        self.state_store = (
            DefensiveStateStore(
                state_file=state_file
            )
        )

        self.executor = (
            ZenithProtocolExecutor(
                state_store=self.state_store
            )
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def build_event(
        self,
        resource="remote_admin"
    ):
        return {
            "username": "jake",
            "source_device": "PC-FIN-01",
            "resource": resource
        }

    def build_decision(
        self,
        protocols=None
    ):
        return {
            "classification":
                "suspicious",

            "response_level":
                4,

            "response_name":
                "containment",

            "incident_severity": {
                "level": 5,
                "name": "critical"
            },

            "recommended_protocols": (
                protocols
                or [
                    "record_event",
                    "increase_monitoring",
                    "open_incident",
                    "alert_administrator",
                    "require_step_up_authentication",
                    "invalidate_active_sessions",
                    "lock_account",
                    "isolate_endpoint"
                ]
            )
        }

    def test_containment_creates_simulated_state(
        self
    ):
        execution = self.executor.execute(
            event=self.build_event(),
            decision=self.build_decision()
        )

        self.assertTrue(
            self.state_store.is_account_locked(
                "jake"
            )
        )

        self.assertTrue(
            self.state_store.is_endpoint_isolated(
                "PC-FIN-01"
            )
        )

        self.assertIsNotNone(
            self.state_store
            .session_invalidation_time(
                "jake"
            )
        )

        applied_protocols = {
            action["protocol"]
            for action
            in execution["applied_actions"]
        }

        self.assertIn(
            "lock_account",
            applied_protocols
        )

        self.assertIn(
            "isolate_endpoint",
            applied_protocols
        )

    def test_state_is_visible_to_another_process_reader(
        self
    ):
        self.executor.execute(
            event=self.build_event(),
            decision=self.build_decision()
        )

        second_store = (
            DefensiveStateStore(
                state_file=(
                    self.state_store
                    .state_file
                )
            )
        )

        self.assertTrue(
            second_store.is_account_locked(
                "jake"
            )
        )

        self.assertTrue(
            second_store.is_endpoint_isolated(
                "PC-FIN-01"
            )
        )

    def test_duplicate_protocol_is_not_applied_twice(
        self
    ):
        first_execution = (
            self.executor.execute(
                event=self.build_event(),
                decision=self.build_decision()
            )
        )

        second_execution = (
            self.executor.execute(
                event=self.build_event(),
                decision=self.build_decision()
            )
        )

        self.assertGreater(
            len(
                first_execution[
                    "applied_actions"
                ]
            ),
            0
        )

        self.assertEqual(
            second_execution[
                "applied_actions"
            ],
            []
        )

        self.assertGreater(
            len(
                second_execution[
                    "already_active"
                ]
            ),
            0
        )

    def test_action_can_be_reversed(
        self
    ):
        execution = self.executor.execute(
            event=self.build_event(),
            decision=self.build_decision()
        )

        lock_action = next(
            action
            for action
            in execution["applied_actions"]
            if action["protocol"]
            == "lock_account"
        )

        reversed_action = (
            self.executor.reverse(
                lock_action[
                    "action_id"
                ]
            )
        )

        self.assertEqual(
            reversed_action["status"],
            "reversed"
        )

        self.assertFalse(
            self.state_store.is_account_locked(
                "jake"
            )
        )

        action_history = (
            self.state_store.list_actions()
        )

        self.assertIn(
            "reversed",
            {
                action["status"]
                for action
                in action_history
            }
        )

    def test_protocol_without_target_is_skipped(
        self
    ):
        execution = self.executor.execute(
            event=self.build_event(
                resource=None
            ),
            decision=self.build_decision(
                protocols=[
                    "protect_target_resource"
                ]
            )
        )

        self.assertEqual(
            execution[
                "applied_actions"
            ],
            []
        )

        self.assertEqual(
            execution[
                "skipped_protocols"
            ][0][
                "protocol"
            ],
            "protect_target_resource"
        )


if __name__ == "__main__":
    unittest.main()