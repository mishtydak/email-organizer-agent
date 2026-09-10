from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Task:
    description: str
    deadline: str | None = None
    assigned_to: str | None = None
    confidence: float | None = None
    status: str = "pending"


@dataclass
class FollowUp:
    email_subject: str
    reminder_at: datetime
    status: str = "pending"


def create_task(description, deadline=None, assigned_to=None, confidence=None):
    return Task(
        description=description,
        deadline=deadline,
        assigned_to=assigned_to,
        confidence=confidence
    )


def schedule_follow_up(email, days=2):
    return FollowUp(
        email_subject=email.subject,
        reminder_at=datetime.now() + timedelta(days=days)
    )


def get_due_follow_ups(follow_ups):
    now = datetime.now()

    return [
        item
        for item in follow_ups
        if item.reminder_at <= now
        and item.status == "pending"
    ]


def mark_task_complete(task, confirmed=False):
    if not confirmed:
        print("Task cannot be completed without confirmation.")
        return task

    task.status = "completed"
    return task