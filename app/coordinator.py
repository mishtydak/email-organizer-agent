from dataclasses import dataclass


@dataclass
class Plan:
    goal: str
    scope: str
    priority_focus: str
    output: str
    steps: list[str]


def clarify_request():
    print("\nI need a few details before creating the plan.")

    scope = input(
        "\n1. Which emails should be organized? "
        "(e.g. unread emails, today's emails, last week's emails): "
    )

    priority_focus = input(
        "\n2. What should be prioritized? "
        "(e.g. deadlines, urgent requests, admin emails): "
    )

    output = input(
        "\n3. What should the final result contain? "
        "(e.g. categories, priorities, action items, draft replies): "
    )

    return scope, priority_focus, output


def propose_plan(scope, priority_focus, output):
    return Plan(
        goal="Organize and triage the inbox",
        scope=scope,
        priority_focus=priority_focus,
        output=output,
        steps=[
            "Collect the selected emails",
            "Classify the emails",
            "Assign priority",
            "Identify important action items",
            "Prepare the requested output",
            "Present the result for human review"
        ]
    )


def display_plan(plan):
    print("\n========== PROPOSED PLAN ==========")
    print(f"Goal: {plan.goal}")
    print(f"Scope: {plan.scope}")
    print(f"Priority focus: {plan.priority_focus}")
    print(f"Output: {plan.output}")

    print("\nSteps:")
    for i, step in enumerate(plan.steps, start=1):
        print(f"{i}. {step}")

    print("===================================\n")


def revise_plan(plan):
    feedback = input(
        "Would you like to change anything in the plan? "
        "(yes/no): "
    )

    if feedback.lower() != "yes":
        return plan

    change = input("What would you like to change? ")

    plan.steps.append(f"User requested change: {change}")

    return plan


def run_coordinator():
    print("=== Email Organizer Coordinator ===")

    user_request = input("\nWhat would you like me to do? ")

    print(f"\nYour request: {user_request}")

    scope, priority_focus, output = clarify_request()

    plan = propose_plan(
        scope,
        priority_focus,
        output
    )

    display_plan(plan)

    plan = revise_plan(plan)

    print("\n========== FINAL PLAN ==========")
    display_plan(plan)


if __name__ == "__main__":
    run_coordinator()