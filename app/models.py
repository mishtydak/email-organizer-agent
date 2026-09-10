from dataclasses import dataclass


@dataclass
class Email:
    sender: str
    subject: str
    body: str
    message_id: str | None = None
    thread_id: str | None = None