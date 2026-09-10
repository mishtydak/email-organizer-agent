from models import Email
from datetime import datetime


# Temporary inbox data
INBOX = [
    Email(
        sender="student@gmail.com",
        subject="Project extension",
        body="Sir, can I get two additional days to submit my project?"
    ),
    Email(
        sender="admin@university.edu",
        subject="Faculty submission deadline",
        body="All faculty members must submit the accreditation report by tomorrow."
    ),
    Email(
        sender="researcher@iit.edu",
        subject="Research meeting",
        body="Can we schedule a meeting next week to discuss our joint research paper?"
    )
]


def read_inbox() -> list[Email]:
    """
    Tool that reads emails from the inbox.
    """
    return INBOX


CONTACTS = {
    "student@gmail.com": {
        "name": "Student",
        "category": "Student",
        "previous_replies": [
            "Please submit the project report before the deadline."
        ]
    },
    "admin@university.edu": {
        "name": "University Admin",
        "category": "Admin",
        "previous_replies": [
            "Thank you for the accreditation update."
        ]
    },
    "researcher@iit.edu": {
        "name": "Research Collaborator",
        "category": "Collaborator",
        "previous_replies": [
            "I am available for research discussions next week."
        ]
    }
}


def lookup_contact(email_address: str) -> dict | None:
    """
    Tool that retrieves contact information
    and previous replies for an email address.
    """
    return CONTACTS.get(email_address)

def check_deadline(deadline: str) -> int | None:
    """
    Tool that calculates how many days remain until a deadline.

    Expected format: YYYY-MM-DD
    """
    try:
        deadline_date = datetime.strptime(
            deadline,
            "%Y-%m-%d"
        ).date()

        today = datetime.today().date()

        return (deadline_date - today).days

    except ValueError:
        return None
    
def get_email_context(email: Email) -> dict:
    """
    Tool that gathers the information needed
    to reason about a single email.
    """

    contact = lookup_contact(email.sender)

    return {
        "email": email,
        "contact": contact
    }