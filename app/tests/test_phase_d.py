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


from review_queue import (
    create_review_item,
    edit_review_item,
    approve_review_item,
    reject_review_item,
    ReviewState
)

from audit import get_audit_log


def test_review_workflow():

    print(
        "\n========== PHASE D REVIEW TEST ==========\n"
    )

    item = create_review_item(
        recipient="student@example.com",
        subject="Re: Project Extension",
        body=(
            "Dear Student,\n\n"
            "Your extension request has been noted.\n\n"
            "Regards,\nFaculty"
        )
    )

    print("Initial state:", item.state.value)

    assert item.state == ReviewState.DRAFT

    # Faculty edits draft
    edit_review_item(
        item,
        body=(
            "Dear Student,\n\n"
            "Your extension request has been approved. "
            "Please submit the revised project by Friday.\n\n"
            "Regards,\nFaculty"
        )
    )

    print("\nEdited draft:")
    print(item.body)

    assert "approved" in item.body

    # Approve
    approve_review_item(
        item,
        reviewer="faculty"
    )

    print(
        "\nAfter approval:",
        item.state.value
    )

    assert item.state == ReviewState.APPROVED

    # Audit check
    logs = get_audit_log()

    assert len(logs) == 2

    assert logs[1].action == "approve_email"

    print(
        "\nAudit log entry:",
        logs[1]
    )

    print(
        "\nPASS: Review workflow works."
    )


def test_unapproved_email_blocked():

    print(
        "\n========== APPROVAL GUARD TEST ==========\n"
    )

    item = create_review_item(
        recipient="student@example.com",
        subject="Test",
        body="Test email"
    )

    try:

        # Import only here so the test does not
        # accidentally send anything.
        from gmail_sender import send_approved_email

        send_approved_email(
            item,
            gmail_sender=None
        )

        assert False, (
            "Unapproved email was allowed to send."
        )

    except PermissionError as error:

        print(
            "Correctly blocked:",
            error
        )

    print(
        "\nPASS: Unapproved sending blocked."
    )


if __name__ == "__main__":

    test_review_workflow()

    test_unapproved_email_blocked()

    print(
        "\n=========================================="
    )

    print(
        "PASS: PHASE D CORE TESTS PASSED"
    )