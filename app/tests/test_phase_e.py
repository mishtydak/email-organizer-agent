import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from models import Email

from memory import LONG_TERM_MEMORY

from grounding import (
    retrieve_evidence,
    validate_grounding,
    create_grounded_output
)

from governance import (
    GovernedOutput,
    ApprovalState,
    approve_output,
    update_output,
    rollback
)


def test_grounding():

    print(
        "\n========== GROUNDING TEST ==========\n"
    )

    email = Email(
        sender="student@university.edu",
        subject="Project Extension",
        body=(
            "I am requesting an extension "
            "for my project."
        )
    )

    evidence = retrieve_evidence(
        email,
        LONG_TERM_MEMORY
    )

    print("Evidence found:")

    for item in evidence:
        print(
            "-",
            item.content
        )

    assert len(evidence) > 0

    result = create_grounded_output(
        email,
        LONG_TERM_MEMORY
    )

    assert result["status"] == "grounded"

    errors = validate_grounding(
        result,
        evidence
    )

    assert errors == []

    print(
        "\nPASS: Grounding validation works."
    )


def test_ungrounded_output_rejected():

    print(
        "\n========== UNGROUNDED TEST ==========\n"
    )

    email = Email(
        sender="unknown@example.com",
        subject="Random Topic",
        body=(
            "This is unrelated "
            "to previous conversations."
        )
    )

    result = create_grounded_output(
        email,
        LONG_TERM_MEMORY
    )

    print(result)

    assert result["status"] == "rejected"

    print(
        "\nPASS: Ungrounded output rejected."
    )


def test_governance():

    print(
        "\n========== GOVERNANCE TEST ==========\n"
    )

    grounded_content = {
        "status": "grounded",
        "subject": "Project Extension",
        "evidence": [
            {
                "source": "prior_history",
                "content": (
                    "Student requested "
                    "a two-day extension."
                ),
                "relevance": 1
            }
        ]
    }

    output = GovernedOutput(
        content=grounded_content
    )

    assert (
        output.state
        == ApprovalState.DRAFT
    )

    print(
        "Initial state:",
        output.state.value
    )

    # Edit
    edited_content = {
        **grounded_content,
        "review_note": (
            "Faculty reviewed the request."
        )
    }

    update_output(
        output,
        edited_content,
        actor="faculty"
    )

    print(
        "Version after edit:",
        output.version
    )

    assert output.version == 2

    # Approve
    approve_output(
        output,
        actor="faculty"
    )

    print(
        "State after approval:",
        output.state.value
    )

    assert (
        output.state
        == ApprovalState.APPROVED
    )

    # Rollback should be blocked because
    # only drafts can be edited, but rollback
    # itself is allowed as governance recovery.
    rollback(
        output,
        actor="faculty"
    )

    print(
        "State after rollback:",
        output.state.value
    )

    assert output.version == 1

    print(
        "\nPASS: Governance works."
    )


def test_audit_log():

    print(
        "\n========== AUDIT TEST ==========\n"
    )

    output = GovernedOutput(
        content={
            "subject": "Test"
        }
    )

    approve_output(
        output,
        actor="faculty"
    )

    assert len(
        output.audit_log
    ) == 1

    entry = output.audit_log[0]

    print(entry)

    assert entry["action"] == "approve"
    assert entry["actor"] == "faculty"
    assert "timestamp" in entry
    assert "version" in entry

    print(
        "\nPASS: Audit logging works."
    )


if __name__ == "__main__":

    test_grounding()

    test_ungrounded_output_rejected()

    test_governance()

    test_audit_log()

    print(
        "\n===================================="
    )

    print(
        "PASS: PHASE E COMPLETE"
    )

    print(
        "===================================="
    )