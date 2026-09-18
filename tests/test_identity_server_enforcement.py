import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from hq import identity_server

from simulation.defensive_state import (
    DefensiveStateStore
)


class IdentityServerEnforcementTests(
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

        self.state_patch = patch(
            "hq.identity_server."
            "DEFENSIVE_STATE",
            self.state_store
        )

        self.state_patch.start()

        identity_server.FAILED_ATTEMPTS.clear()
        identity_server.LOCKED_ACCOUNTS.clear()
        identity_server.SESSIONS.clear()

        identity_server.USERS[
            "jake"
        ][
            "password"
        ] = "Zenith-jake-2026!"

    def tearDown(self):
        self.state_patch.stop()
        self.temporary_directory.cleanup()

    def apply_user_protocol(
        self,
        protocol
    ):
        return (
            self.state_store.apply_action(
                protocol=protocol,
                target_type="user",
                target="jake",
                reason="Test containment"
            )
        )

    def authenticate_jake(self):
        return (
            identity_server
            .authenticate_user(
                username="jake",
                password=(
                    "Zenith-jake-2026!"
                ),
                source_device="PC-FIN-01"
            )
        )

    def test_simulated_account_lock_blocks_login(
        self
    ):
        self.apply_user_protocol(
            "lock_account"
        )

        response = (
            self.authenticate_jake()
        )

        self.assertFalse(
            response["authenticated"]
        )

        self.assertEqual(
            response["reason"],
            "Account locked by Zenith"
        )

    def test_isolated_endpoint_fails_validation(
        self
    ):
        self.state_store.apply_action(
            protocol="isolate_endpoint",
            target_type="endpoint",
            target="PC-FIN-01",
            reason="Test containment"
        )

        response = (
            identity_server
            .validate_endpoint(
                username="jake",
                device_id="PC-FIN-01"
            )
        )

        self.assertFalse(
            response["valid"]
        )

        self.assertEqual(
            response["reason"],
            "Endpoint isolated by Zenith"
        )

    def test_existing_session_is_invalidated(
        self
    ):
        login_response = (
            self.authenticate_jake()
        )

        session_token = (
            login_response[
                "session_token"
            ]
        )

        self.apply_user_protocol(
            "invalidate_active_sessions"
        )

        validation = (
            identity_server
            .validate_session(
                session_token
            )
        )

        self.assertFalse(
            validation["valid"]
        )

        self.assertEqual(
            validation["reason"],
            "Session invalidated by Zenith"
        )

        self.assertEqual(
            validation["username"],
            "jake"
        )

    def test_new_session_after_invalidation_is_valid(
        self
    ):
        self.apply_user_protocol(
            "invalidate_active_sessions"
        )

        login_response = (
            self.authenticate_jake()
        )

        self.assertTrue(
            login_response[
                "authenticated"
            ]
        )

        validation = (
            identity_server
            .validate_session(
                login_response[
                    "session_token"
                ]
            )
        )

        self.assertTrue(
            validation["valid"]
        )

    def test_step_up_requirement_blocks_normal_login(
        self
    ):
        self.apply_user_protocol(
            "require_step_up_authentication"
        )

        response = (
            self.authenticate_jake()
        )

        self.assertFalse(
            response["authenticated"]
        )

        self.assertTrue(
            response[
                "step_up_required"
            ]
        )

        self.assertEqual(
            response["reason"],
            (
                "Additional identity verification "
                "required by Zenith"
            )
        )


if __name__ == "__main__":
    unittest.main()