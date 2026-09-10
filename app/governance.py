from dataclasses import dataclass, field
from enum import Enum
from copy import deepcopy
from datetime import datetime


class ApprovalState(Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class GovernedOutput:

    content: dict

    state: ApprovalState = (
        ApprovalState.DRAFT
    )

    version: int = 1

    history: list = field(
        default_factory=list
    )

    audit_log: list = field(
        default_factory=list
    )


def log_action(
    output,
    action,
    actor
):

    output.audit_log.append(
        {
            "action": action,
            "actor": actor,
            "timestamp": datetime.now(),
            "version": output.version
        }
    )


def save_version(output):

    output.history.append(
        {
            "version": output.version,
            "content": deepcopy(
                output.content
            ),
            "state": output.state
        }
    )


def update_output(
    output,
    new_content,
    actor
):

    if output.state != ApprovalState.DRAFT:
        raise PermissionError(
            "Only draft outputs can be edited."
        )

    save_version(output)

    output.content = new_content
    output.version += 1
    output.state = ApprovalState.DRAFT

    log_action(
        output,
        "edit",
        actor
    )

    return output


def approve_output(
    output,
    actor
):

    if output.state != ApprovalState.DRAFT:
        raise PermissionError(
            "Only draft outputs can be approved."
        )

    output.state = ApprovalState.APPROVED

    log_action(
        output,
        "approve",
        actor
    )

    return output


def reject_output(
    output,
    actor
):

    if output.state != ApprovalState.DRAFT:
        raise PermissionError(
            "Only draft outputs can be rejected."
        )

    output.state = ApprovalState.REJECTED

    log_action(
        output,
        "reject",
        actor
    )

    return output


def rollback(
    output,
    actor
):

    if not output.history:
        raise ValueError(
            "No previous version available."
        )

    previous = output.history.pop()

    output.content = deepcopy(
        previous["content"]
    )

    output.version = (
        previous["version"]
    )

    output.state = (
        previous["state"]
    )

    log_action(
        output,
        "rollback",
        actor
    )

    return output