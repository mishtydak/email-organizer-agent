from dataclasses import dataclass
from enum import Enum
from audit import log_action

class ReviewState(Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"


@dataclass
class ReviewItem:
    recipient: str
    subject: str
    body: str
    state: ReviewState = ReviewState.DRAFT
    reviewer: str | None = None


def create_review_item(
    recipient,
    subject,
    body
):
    item = ReviewItem(
        recipient=recipient,
        subject=subject,
        body=body
    )
    log_action(
        action="create_draft",
        actor="system",
        recipient=recipient,
        subject=subject
    )
    return item


def edit_review_item(
    item,
    subject=None,
    body=None
):
    if item.state != ReviewState.DRAFT:
        raise PermissionError(
            "Only draft items can be edited."
        )

    if subject is not None:
        item.subject = subject

    if body is not None:
        item.body = body
        
    item.version = getattr(item, 'version', 1) + 1
    
    log_action(
        action="edit_draft",
        actor="Faculty User",
        recipient=item.recipient,
        subject=item.subject
    )

    return item

def approve_review_item(
    item,
    reviewer
):
    if item.state != ReviewState.DRAFT:
        raise PermissionError(
            "Only draft items can be approved."
        )

    item.state = ReviewState.APPROVED
    item.reviewer = reviewer

    log_action(
        action="approve_email",
        actor=reviewer,
        recipient=item.recipient,
        subject=item.subject
    )

    return item

def reject_review_item(
    item,
    reviewer
):
    if item.state != ReviewState.DRAFT:
        raise PermissionError(
            "Only draft items can be rejected."
        )

    item.state = ReviewState.REJECTED
    item.reviewer = reviewer

    log_action(
        action="reject_email",
        actor=reviewer,
        recipient=item.recipient,
        subject=item.subject
    )

    return item

def mark_as_sent(item):

    if item.state != ReviewState.APPROVED:
        raise PermissionError(
            "Only approved drafts can be marked as sent."
        )

    item.state = ReviewState.SENT

    log_action(
        action="send_email",
        actor="system",
        recipient=item.recipient,
        subject=item.subject
    )

    return item