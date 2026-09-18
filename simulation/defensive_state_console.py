from simulation.defensive_state import (
    DefensiveStateStore
)


def format_label(value):
    if value is None:
        return "Unknown"

    return str(value).replace(
        "_",
        " "
    ).title()


def display_actions(
    state_store,
    active_only=False
):
    actions = (
        state_store.list_actions(
            active_only=active_only
        )
    )

    heading = (
        "ACTIVE DEFENSIVE ACTIONS"
        if active_only
        else "DEFENSIVE ACTION HISTORY"
    )

    print(
        f"\n{heading}"
    )

    print(
        "=" * len(heading)
    )

    if not actions:
        print(
            "No defensive actions found."
        )

        return []

    for number, action in enumerate(
        actions,
        start=1
    ):
        print(
            f"\nAction #{number}"
        )

        print(
            "-" * 30
        )

        print(
            "Protocol: "
            f"{format_label(action['protocol'])}"
        )

        print(
            "Target:   "
            f"{format_label(action['target_type'])} "
            f"- {action['target']}"
        )

        print(
            "Status:   "
            f"{format_label(action['status'])}"
        )

        print(
            "Applied:  "
            f"{action['applied_at']}"
        )

        if action.get(
            "reversed_at"
        ):
            print(
                "Reversed: "
                f"{action['reversed_at']}"
            )

        print(
            "Reason:   "
            f"{action['reason']}"
        )

        print(
            "Action ID:"
            f" {action['action_id']}"
        )

    return actions


def reverse_action_by_number(
    state_store,
    selection
):
    active_actions = (
        state_store.list_actions(
            active_only=True
        )
    )

    try:
        index = int(selection) - 1

    except ValueError:
        return {
            "success": False,
            "reason": (
                "Selection must be a number."
            )
        }

    if (
        index < 0
        or index >= len(
            active_actions
        )
    ):
        return {
            "success": False,
            "reason": (
                "Defensive action selection "
                "does not exist."
            )
        }

    selected_action = (
        active_actions[index]
    )

    reversed_action = (
        state_store.reverse_action(
            selected_action[
                "action_id"
            ]
        )
    )

    if reversed_action is None:
        return {
            "success": False,
            "reason": (
                "Defensive action could not "
                "be found."
            )
        }

    return {
        "success": True,
        "reason": (
            f"{format_label(
                reversed_action['protocol']
            )} was reversed for "
            f"{reversed_action['target']}."
        ),
        "action": reversed_action
    }


def reset_scenario_state(
    state_store,
    confirmation
):
    if confirmation != "RESET":
        return {
            "success": False,
            "reason": (
                "Reset cancelled. Confirmation "
                "must exactly match RESET."
            )
        }

    state_store.reset()

    return {
        "success": True,
        "reason": (
            "All simulated defensive state "
            "was reset."
        )
    }


def main():
    state_store = (
        DefensiveStateStore()
    )

    while True:
        print(
            "\nZENITH DEFENSIVE STATE"
        )

        print(
            "======================"
        )

        print(
            "1. View active actions"
        )

        print(
            "2. View action history"
        )

        print(
            "3. Reverse an active action"
        )

        print(
            "4. Reset scenario state"
        )

        print(
            "5. Exit"
        )

        choice = input(
            "\nSelect an option: "
        ).strip()

        if choice == "1":
            display_actions(
                state_store,
                active_only=True
            )

        elif choice == "2":
            display_actions(
                state_store,
                active_only=False
            )

        elif choice == "3":
            active_actions = (
                display_actions(
                    state_store,
                    active_only=True
                )
            )

            if not active_actions:
                continue

            selection = input(
                "\nAction number to reverse: "
            ).strip()

            result = (
                reverse_action_by_number(
                    state_store,
                    selection
                )
            )

            print(
                f"\n{result['reason']}"
            )

        elif choice == "4":
            print(
                "\nThis clears the current "
                "simulation state and its "
                "action history."
            )

            confirmation = input(
                "Type RESET to continue: "
            ).strip()

            result = (
                reset_scenario_state(
                    state_store,
                    confirmation
                )
            )

            print(
                f"\n{result['reason']}"
            )

        elif choice == "5":
            print(
                "Defensive-state console closed."
            )

            break

        else:
            print(
                "Invalid option."
            )


if __name__ == "__main__":
    main()