from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class FollowUp:
    email_subject: str
    reminder_at: datetime
    status: str = "pending"


def schedule_follow_up(email, days=2):
    reminder_at = datetime.now() + timedelta(days=days)

    return FollowUp(
        email_subject=email.subject,
        reminder_at=reminder_at
    )


def get_due_follow_ups(follow_ups):
    now = datetime.now()

    return [
        follow_up
        for follow_up in follow_ups
        if follow_up.reminder_at <= now
        and follow_up.status == "pending"
    ]