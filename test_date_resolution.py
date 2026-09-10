import sys
import os
import unittest
from datetime import datetime, time, timedelta
from unittest.mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
from calendar_agent import resolve_datetime, propose_meeting_slots_with_preference

class TestDateResolution(unittest.TestCase):

    def test_resolve_datetime(self):
        # Suppose today is Wednesday, Sept 9
        reference_date = datetime(2026, 9, 9).date() 
        # Wednesday is index 2. Friday is index 4.
        
        # Friday 3 pm
        dt = resolve_datetime("Friday", "3 pm", reference_date)
        self.assertEqual(dt.date(), datetime(2026, 9, 11).date())
        self.assertEqual(dt.time(), time(15, 0))
        
        # Monday 10 am (next Monday)
        dt = resolve_datetime("Monday", "10 am", reference_date)
        self.assertEqual(dt.date(), datetime(2026, 9, 14).date())
        self.assertEqual(dt.time(), time(10, 0))

    def test_propose_meeting_slots_free(self):
        connector = MagicMock()
        connector.get_busy_periods.return_value = []
        
        start_date = datetime(2026, 9, 9).date() 
        slots, status = propose_meeting_slots_with_preference(
            connector, start_date, "Friday", "3 pm", days=7
        )
        
        self.assertEqual(status, "AVAILABLE")
        self.assertEqual(slots[0].start, datetime(2026, 9, 11, 15, 0))

    def test_propose_meeting_slots_busy(self):
        connector = MagicMock()
        # Make Friday 3 pm busy
        connector.get_busy_periods.return_value = [
            {
                "start": "2026-09-11T15:00:00Z",
                "end": "2026-09-11T16:00:00Z"
            }
        ]
        
        start_date = datetime(2026, 9, 9).date()
        slots, status = propose_meeting_slots_with_preference(
            connector, start_date, "Friday", "3 pm", days=7
        )
        
        self.assertEqual(status, "BUSY")
        
        # Next same-day free slot near 3 pm should be proposed (e.g. 4 pm or 2:30 pm)
        # Note: 9am-5pm limit in find_available_slots.
        # It should prioritize the same day.
        for slot in slots:
            self.assertEqual(slot.start.date(), datetime(2026, 9, 11).date())
            self.assertNotEqual(slot.start, datetime(2026, 9, 11, 15, 0))
            self.assertNotEqual(slot.start, datetime(2026, 9, 11, 15, 30))

if __name__ == "__main__":
    unittest.main()
