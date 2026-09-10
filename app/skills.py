from dataclasses import dataclass


@dataclass
class Plan:
    goal: str
    scope: str
    priority_focus: str
    output: str
    steps: list[str]


def create_plan(
    goal: str,
    scope: str,
    priority_focus: str,
    output: str
) -> Plan:
    """
    Reusable planning skill.

    Takes case-specific inputs and returns
    a structured plan.
    """

    steps = [
        "Collect the required data",
        "Analyze the data",
        "Apply the requested priority rules",
        "Prepare the requested output",
        "Present the result for human review"
    ]

    return Plan(
        goal=goal,
        scope=scope,
        priority_focus=priority_focus,
        output=output,
        steps=steps
    )
    
    
def format_plan(plan: Plan) -> str:
    """
    Reusable formatting skill.

    Converts a Plan object into a human-readable format.
    """

    result = []

    result.append("========== PLAN ==========")
    result.append(f"Goal: {plan.goal}")
    result.append(f"Scope: {plan.scope}")
    result.append(f"Priority focus: {plan.priority_focus}")
    result.append(f"Output: {plan.output}")

    result.append("\nSteps:")

    for number, step in enumerate(plan.steps, start=1):
        result.append(f"{number}. {step}")

    result.append("==========================")

    return "\n".join(result)