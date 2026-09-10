import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from datetime import date

from meeting_agent import (
    extract_meeting_request,
    get_meeting_proposals,
    confirm_meeting
)

from calendar_connector import GoogleCalendarConnector
from models import Email


email = Email(
    sender="researcher@university.edu",
    subject="Research Meeting",
    body=(
        "Can we schedule a meeting to discuss "
        "our research paper?"
    )
)


print("\n========== MEETING REQUEST ==========")

meeting_request = extract_meeting_request(email)

print(meeting_request)


if meeting_request.meeting_requested:

    print(
        "\n========== CHECKING CALENDAR =========="
    )

    calendar = GoogleCalendarConnector()

    proposals = get_meeting_proposals(
        meeting_request=meeting_request,
        calendar_connector=calendar,
        start_date=date.today(),
        days=5
    )

    print(
        "\n========== PROPOSED SLOTS =========="
    )

    for index, slot in enumerate(
        proposals,
        start=1
    ):
        print(
            f"{index}. "
            f"{slot.start} -> {slot.end}"
        )

    assert len(proposals) > 0

    print(
        "\nPASS: Available meeting slots found."
    )