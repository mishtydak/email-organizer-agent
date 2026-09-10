from grounding import (
    create_grounded_output
)

from governance import (
    GovernedOutput,
    approve_output,
    reject_output,
    update_output,
    rollback
)


def run_grounding_check(
    email,
    memory_items
):

    result = create_grounded_output(
        email,
        memory_items
    )

    if result["status"] != "grounded":

        print(
            "GROUNDING FAILED:"
        )

        print(
            result["reason"]
        )

        return None

    print(
        "GROUNDING PASSED"
    )

    for evidence in result["evidence"]:

        print(
            f"- {evidence['content']}"
        )

    return result


def create_governed_draft(
    grounded_result
):

    if grounded_result is None:
        raise ValueError(
            "Cannot govern an ungrounded output."
        )

    return GovernedOutput(
        content=grounded_result
    )


def approve_draft(
    output,
    reviewer
):

    return approve_output(
        output,
        reviewer
    )


def reject_draft(
    output,
    reviewer
):

    return reject_output(
        output,
        reviewer
    )


def edit_draft(
    output,
    new_content,
    editor
):

    return update_output(
        output,
        new_content,
        editor
    )


def rollback_draft(
    output,
    actor
):

    return rollback(
        output,
        actor
    )