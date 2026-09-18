import io
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path

from simulation.defensive_state import (
    DefensiveStateStore
)

from simulation.defensive_state_console import (
    display_actions,
    reset_scenario_state,
    reverse_action_by_number
)


class DefensiveStateConsoleTests(
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

        self.state_store.apply_action(
            protocol="lock_account",
            target_type="user",
            target="jake",
            reason="Test containment"
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_active_action_is_visible(
        self
    ):
        output = io.StringIO()

        with redirect_stdout(
            output
        ):
            actions = display_actions(
                self.state_store,
                active_only=True
            )

        rendered_output = (
            output.getvalue()
        )

        self.assertEqual(
            len(actions),
            1
        )

        self.assertIn(
            "Lock Account",
            rendered_output
        )

        self.assertIn(
            "jake",
            rendered_output
        )

        self.assertIn(
            "Active",
            rendered_output
        )

    def test_action_can_be_reversed_by_number(
        self
    ):
        result = (
            reverse_action_by_number(
                self.state_store,
                "1"
            )
        )

        self.assertTrue(
            result["success"]
        )

        self.assertFalse(
            self.state_store.is_account_locked(
                "jake"
            )
        )

        history = (
            self.state_store.list_actions()
        )

        self.assertEqual(
            history[0]["status"],
            "reversed"
        )

    def test_scenario_reset_requires_confirmation(
        self
    ):
        cancelled_result = (
            reset_scenario_state(
                self.state_store,
                "reset"
            )
        )

        self.assertFalse(
            cancelled_result[
                "success"
            ]
        )

        self.assertTrue(
            self.state_store.is_account_locked(
                "jake"
            )
        )

        reset_result = (
            reset_scenario_state(
                self.state_store,
                "RESET"
            )
        )

        self.assertTrue(
            reset_result[
                "success"
            ]
        )

        self.assertEqual(
            self.state_store.list_actions(),
            []
        )


if __name__ == "__main__":
    unittest.main()