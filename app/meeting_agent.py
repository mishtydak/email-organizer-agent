from dataclasses import dataclass
from calendar_agent import propose_meeting_slots_with_preference

@dataclass
class MeetingRequest:
    meeting_requested: bool
    proposed_date: str | None
    proposed_time: str | None
    purpose: str | None


def extract_meeting_request(email):
    text = f"{email.subject} {email.body}".lower()

    meeting_words = [
        "meeting",
        "meet",
        "schedule",
        "discuss",
        "call"
    ]

    meeting_requested = any(word in text for word in meeting_words)

    if not meeting_requested:
        return MeetingRequest(
            meeting_requested=False,
            proposed_date=None,
            proposed_time=None,
            purpose=None
        )

    proposed_date = None
    proposed_time = None

    for day in [
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"
    ]:
        if day in text:
            proposed_date = day.capitalize()
            break

    for time in ["9 am", "10 am", "11 am", "12 pm",
                 "1 pm", "2 pm", "3 pm", "4 pm", "5 pm"]:
        if time in text:
            proposed_time = time
            break

    purpose = email.subject if email.subject else None

    return MeetingRequest(
        meeting_requested=True,
        proposed_date=proposed_date,
        proposed_time=proposed_time,
        purpose=purpose
    )
    
def get_meeting_proposals(
    meeting_request,
    calendar_connector,
    start_date,
    days=5
):
    if not meeting_request.meeting_requested:
        return []

    return propose_meeting_slots_with_preference(
        calendar_connector=calendar_connector,
        start_date=start_date,
        proposed_date_str=meeting_request.proposed_date,
        proposed_time_str=meeting_request.proposed_time,
        days=days,
        duration_minutes=30,
        number_of_slots=5
    )
    
    
def confirm_meeting(
    meeting_request,
    selected_slot,
    approved=False
):
    if not approved:
        raise PermissionError(
            "Meeting cannot be confirmed "
            "without faculty approval."
        )

    return {
        "status": "approved",
        "subject": meeting_request.purpose,
        "start": selected_slot.start,
        "end": selected_slot.end
    }