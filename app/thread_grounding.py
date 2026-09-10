from dataclasses import dataclass

from gmail_thread import (
    ThreadMessage,
    parse_thread_messages
)


@dataclass
class ThreadEvidence:
    message_id: str
    sender: str
    subject: str
    content: str
    relevance: float


def calculate_relevance(
    current_email,
    previous_message
):

    score = 0

    current_subject = (
        current_email.subject
        .lower()
    )

    previous_subject = (
        previous_message.subject
        .lower()
    )

    if current_subject and (
        current_subject
        in previous_subject
        or previous_subject
        in current_subject
    ):
        score += 2

    current_words = set(
        current_email.body
        .lower()
        .split()
    )

    previous_words = set(
        previous_message.body
        .lower()
        .split()
    )

    common_words = (
        current_words
        & previous_words
    )

    score += min(
        len(common_words),
        5
    )

    return score


def retrieve_thread_evidence(
    current_email,
    thread_messages
):

    evidence = []

    for message in thread_messages:

        # Don't use the current message
        # as its own evidence.
        if (
            message.message_id
            == current_email.message_id
        ):
            continue

        score = calculate_relevance(
            current_email,
            message
        )

        if score > 0:

            evidence.append(
                ThreadEvidence(
                    message_id=(
                        message.message_id
                    ),
                    sender=message.sender,
                    subject=message.subject,
                    content=message.body,
                    relevance=score
                )
            )

    return sorted(
        evidence,
        key=lambda x: x.relevance,
        reverse=True
    )


def ground_email_from_thread(
    current_email,
    raw_messages
):

    thread_messages = (
        parse_thread_messages(
            raw_messages
        )
    )

    evidence = retrieve_thread_evidence(
        current_email,
        thread_messages
    )

    if not evidence:

        return {
            "status": "rejected",
            "reason": (
                "No relevant prior "
                "message found in Gmail thread."
            ),
            "evidence": []
        }

    return {
        "status": "grounded",
        "thread_id": (
            current_email.thread_id
        ),
        "evidence": [
            {
                "message_id": item.message_id,
                "sender": item.sender,
                "subject": item.subject,
                "content": item.content,
                "relevance": item.relevance
            }
            for item in evidence
        ]
    }