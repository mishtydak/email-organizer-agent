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

from calendar_connector import GoogleCalendarConnector
from calendar_agent import find_available_slots


def test_slot_generation_with_mock_busy_periods():

    busy_periods = [
        {
            "start": "2026-09-10T10:00:00+00:00",
            "end": "2026-09-10T11:00:00+00:00"
        }
    ]

    slots = find_available_slots(
        busy_periods=busy_periods,
        start_date=date(2026, 9, 10),
        days=1,
        duration_minutes=30
    )

    for slot in slots:
        print(
            slot.start,
            "->",
            slot.end
        )

    assert len(slots) > 0

    busy_start = 10 * 60
    busy_end = 11 * 60

    for slot in slots:

     slot_start = (
        slot.start.hour * 60
        + slot.start.minute
     )

     slot_end = (
        slot.end.hour * 60
        + slot.end.minute
     )

     assert not (
         slot_start < busy_end
        and slot_end > busy_start
     )


def test_google_calendar_connection():

    calendar = GoogleCalendarConnector()

    print(
        "\nGoogle Calendar connection successful."
    )

    return calendar


if __name__ == "__main__":

    print(
        "\n========== PHASE C TEST ==========\n"
    )

    test_slot_generation_with_mock_busy_periods()

    test_google_calendar_connection()

    print(
        "\nPASS: Phase C Calendar integration works."
    )