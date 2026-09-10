from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuditEntry:
    action: str
    recipient: str | None
    subject: str | None
    actor: str
    timestamp: datetime


AUDIT_LOG = []


def log_action(
    action,
    actor,
    recipient=None,
    subject=None
):

    entry = AuditEntry(
        action=action,
        recipient=recipient,
        subject=subject,
        actor=actor,
        timestamp=datetime.now()
    )

    AUDIT_LOG.append(entry)

    return entry


def get_audit_log():
    return list(AUDIT_LOG)