from dataclasses import dataclass


@dataclass
class AcceptanceCriterion:
    name: str
    description: str


@dataclass
class AgentSpec:
    name: str
    goal: str
    acceptance_criteria: list[AcceptanceCriterion]


EMAIL_TRIAGE_SPEC = AgentSpec(
    name="Email Triage Agent",
    goal="Produce a validated triage result for each email.",
    acceptance_criteria=[
        AcceptanceCriterion(
            name="sender",
            description="Every email must have a sender."
        ),
        AcceptanceCriterion(
            name="subject",
            description="Every email must have a subject."
        ),
        AcceptanceCriterion(
            name="priority",
            description="Priority must be Critical, High, Medium, or Low."
        ),
        AcceptanceCriterion(
            name="grounding",
            description="Relevant output must contain supporting evidence."
        )
    ]
)



def check_acceptance(draft: dict) -> list[str]:
    errors = []

    if not draft.get("sender"):
        errors.append("Missing sender")

    if not draft.get("subject"):
        errors.append("Missing subject")

    if draft.get("priority") not in {
        "Critical",
        "High",
        "Medium",
        "Low"
    }:
        errors.append("Invalid priority")

    if "evidence" not in draft:
        errors.append("Missing grounding evidence")

    return errors


def validate_output(drafts: list[dict]) -> tuple[bool, list[str]]:
    errors = []

    for index, draft in enumerate(drafts):
        draft_errors = check_acceptance(draft)

        for error in draft_errors:
            errors.append(f"Email {index}: {error}")

    return len(errors) == 0, errors


def run_acceptance_suite(drafts: list[dict]) -> bool:
    passed, errors = validate_output(drafts)

    print("\n========== ACCEPTANCE SUITE ==========")

    if passed:
        print("PASS: All acceptance criteria satisfied.")
    else:
        print("FAIL: Acceptance criteria not satisfied.")

        for error in errors:
            print(f"- {error}")

    print("======================================")

    return passed