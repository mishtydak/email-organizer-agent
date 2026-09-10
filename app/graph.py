from dataclasses import dataclass, field
from tools import read_inbox
from retry import retry_operation
from retry import retry_operation
from spec import validate_output
from classifier import classify_email_safe, extract_action_items_safe

@dataclass
class GraphState:
    emails: list = field(default_factory=list)
    classifications: list = field(default_factory=list)
    action_items: list = field(default_factory=list)
    triage_draft: list = field(default_factory=list)
    validation_passed: bool = False
    errors: list = field(default_factory=list)
    



def ingest_inbox(state: GraphState) -> GraphState:
    state.emails = read_inbox()
    return state


def run_action_with_retry(action, state):
    return retry_operation(
        lambda: action(state),
        max_retries=2
    )

def classify_emails(state: GraphState) -> GraphState:
    state.classifications = []

    for email in state.emails:
        classification = classify_email_safe(email)

        state.classifications.append(
            {
                "sender_category": classification.sender_category,
                "email_type": classification.email_type,
                "priority": classification.priority
            }
        )

    return state

def extract_actions(state: GraphState) -> GraphState:
    state.action_items = []

    for email in state.emails:
        extraction = extract_action_items_safe(email)

        state.action_items.append(
            {
                "email": email,
                "action_items": extraction.action_items
            }
        )

    return state


def create_triage_draft(state: GraphState) -> GraphState:
    for email, classification, actions in zip(
        state.emails,
        state.classifications,
        state.action_items
    ):
        draft = {
            "sender": email.sender,
            "subject": email.subject,
            "sender_category": classification["sender_category"],
            "email_type": classification["email_type"],
            "priority": classification["priority"],
            "action_items": actions["action_items"]
        }

        state.triage_draft.append(draft)

    return state


def validate_triage(state: GraphState) -> GraphState:
    state.errors = []

    for index, draft in enumerate(state.triage_draft):
        if not draft["sender"]:
            state.errors.append(
                f"Email {index}: missing sender"
            )

        if not draft["subject"]:
            state.errors.append(
                f"Email {index}: missing subject"
            )

        if draft["priority"] not in {
            "Critical",
            "High",
            "Medium",
            "Low"
        }:
            state.errors.append(
                f"Email {index}: invalid priority"
            )

    state.validation_passed = len(state.errors) == 0

    return state

def regenerate_triage(state: GraphState) -> GraphState:
    if state.validation_passed:
        return state

    print("\nRegenerating failed triage...")

    state.classifications = []

    for email in state.emails:
        classification = classify_email_safe(email)

        state.classifications.append(
            {
                "sender_category": classification.sender_category,
                "email_type": classification.email_type,
                "priority": classification.priority
            }
        )

    state.triage_draft = []

    return create_triage_draft(state)
def validate_and_regenerate(state: GraphState) -> GraphState:
    state = validate_triage(state)

    if state.validation_passed:
        return state

    def regenerate():
        nonlocal state

        state = regenerate_triage(state)
        state = ground_triage(state)
        state = validate_triage(state)

        if not state.validation_passed:
            raise ValueError(
                "Regenerated triage still failed validation."
            )

        return state

    result = retry_operation(
        regenerate,
        max_retries=2
    )

    if result is None:
        state.validation_passed = False

    return state

def validate_and_recover(state: GraphState) -> GraphState:
    state = validate_triage(state)

    if state.validation_passed:
        return state

    state = regenerate_triage(state)
    state = validate_triage(state)

    return state

def run_graph() -> GraphState:
    state = GraphState()

    state = ingest_inbox(state)
    state = classify_emails(state)
    state = extract_actions(state)
    state = create_triage_draft(state)

    state = ground_triage(state)

    state = validate_and_regenerate(state)

    return state

def test_regeneration():
    state = GraphState()

    state = ingest_inbox(state)
    state = classify_emails(state)
    state = extract_actions(state)
    state = create_triage_draft(state)
    state = ground_triage(state)
    state = validate_grounding(state)

    # Deliberately corrupt one field
    state.triage_draft[0]["priority"] = "INVALID"

    state = validate_triage(state)

    print("\nBefore regeneration:")
    print("Validation:", state.validation_passed)
    print("Errors:", state.errors)

    if not state.validation_passed:
        state = regenerate_triage(state)
        state = validate_triage(state)

    print("\nAfter regeneration:")
    print("Validation:", state.validation_passed)
    print("Errors:", state.errors)
from memory import get_grounding_context



def ground_triage(state: GraphState) -> GraphState:
    for draft, email in zip(state.triage_draft, state.emails):

        evidence = get_grounding_context(
            email.sender,
            email.subject,
            email.body
        )

        draft["evidence"] = [
            memory.content
            for memory in evidence
        ]

    return state


def validate_grounding(state: GraphState) -> GraphState:
    grounding_errors = []

    for index, draft in enumerate(state.triage_draft):
        evidence = draft.get("evidence", [])

        if not evidence:
            grounding_errors.append(
                f"Email {index}: output is not grounded in prior history"
            )

    if grounding_errors:
        state.errors.extend(grounding_errors)
        state.validation_passed = False

    return state


if __name__ == "__main__":
    test_regeneration()