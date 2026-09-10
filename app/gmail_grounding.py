from gmail_thread import parse_thread_messages
from thread_grounding import (
    retrieve_thread_evidence
)


class GmailThreadGrounder:

    def __init__(
        self,
        gmail_connector
    ):
        self.gmail = gmail_connector

    def ground_email(
        self,
        email
    ):

        if not email.thread_id:

            return {
                "status": "rejected",
                "reason": (
                    "Email has no Gmail thread ID."
                ),
                "evidence": []
            }

        messages = (
            self.gmail
            .get_thread_messages(
                email.thread_id
            )
        )

        thread_messages = (
            parse_thread_messages(
                messages
            )
        )

        evidence = retrieve_thread_evidence(
            email,
            thread_messages
        )

        if not evidence:

            return {
                "status": "rejected",
                "reason": (
                    "No relevant prior "
                    "message found in thread."
                ),
                "evidence": []
            }

        return {
            "status": "grounded",
            "thread_id": email.thread_id,
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