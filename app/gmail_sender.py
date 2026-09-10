import base64
from email.mime.text import MIMEText


class GmailSender:

    def __init__(self, gmail_service):
        self.service = gmail_service

    def send(
        self,
        recipient,
        subject,
        body
    ):

        message = MIMEText(body)

        message["to"] = recipient
        message["subject"] = subject

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        result = (
            self.service
            .users()
            .messages()
            .send(
                userId="me",
                body={
                    "raw": encoded_message
                }
            )
            .execute()
        )

        return result
    
from review_queue import (
    ReviewState,
    mark_as_sent
)


def send_approved_email(
    review_item,
    gmail_sender
):

    if review_item.state != ReviewState.APPROVED:
        raise PermissionError(
            "Email cannot be sent without faculty approval."
        )

    result = gmail_sender.send(
        recipient=review_item.recipient,
        subject=review_item.subject,
        body=review_item.body
    )

    mark_as_sent(review_item)

    return result