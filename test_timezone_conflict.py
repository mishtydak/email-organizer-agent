import sys
import os
import unittest
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
from calendar_agent import propose_meeting_slots_with_preference, overlaps, LOCAL_TZ

class TestTimezoneConflict(unittest.TestCase):
    def setUp(self):
        self.mock_connector = MagicMock()

    def test_overlap_rule(self):
        # 1. UTC busy period converted to IST correctly.
        busy_start = datetime.fromisoformat("2026-09-11T09:30:00Z")
        busy_end = datetime.fromisoformat("2026-09-11T10:30:00Z")
        
        # 3:00 PM IST is 09:30 UTC
        slot_3pm = datetime(2026, 9, 11, 15, 0, tzinfo=LOCAL_TZ)
        slot_330pm = datetime(2026, 9, 11, 15, 30, tzinfo=LOCAL_TZ)
        slot_4pm = datetime(2026, 9, 11, 16, 0, tzinfo=LOCAL_TZ)
        slot_430pm = datetime(2026, 9, 11, 16, 30, tzinfo=LOCAL_TZ)
        slot_230pm = datetime(2026, 9, 11, 14, 30, tzinfo=LOCAL_TZ)
        
        # 2. 3:00-3:30 IST overlapping 3:00-4:00 IST (UTC 09:30-10:30)
        self.assertTrue(overlaps(slot_3pm, slot_330pm, busy_start, busy_end))
        
        # 3. 4:00-4:30 IST after 3:00-4:00 IST
        self.assertFalse(overlaps(slot_4pm, slot_430pm, busy_start, busy_end))
        
        # 4. 2:30-3:00 IST touching the beginning
        self.assertFalse(overlaps(slot_230pm, slot_3pm, busy_start, busy_end))
        
    def test_proposed_slot_prioritization(self):
        # Mock Friday 3 PM busy (09:30 UTC)
        self.mock_connector.get_busy_periods.return_value = [
            {
                "start": "2026-09-11T09:30:00Z",
                "end": "2026-09-11T10:30:00Z"
            }
        ]
        
        # We start looking from Wed Sept 9
        start_date = datetime(2026, 9, 9).date()
        
        # 5. Requested Friday 3 PM is checked before generating generic slots.
        slots, status = propose_meeting_slots_with_preference(
            self.mock_connector, start_date, "Friday", "3 pm", days=7
        )
        
        # It should be BUSY
        self.assertEqual(status, "BUSY")
        
        # The generated alternatives should be on Friday (Sept 11) and NOT overlap
        # Because we sort by absolute time difference to 3 PM, 
        # 2:30 PM is 30 mins away (free)
        # 4:00 PM is 60 mins away (free)
        # 2:00 PM is 60 mins away (free)
        # Let's verify the first alternative is NOT 3:00 PM and NOT overlapping
        for slot in slots:
            self.assertEqual(slot.start.date(), datetime(2026, 9, 11).date())
            # Ensure it is not 3:00 or 3:30 PM (15:00 or 15:30)
            self.assertNotEqual(slot.start.time(), time(15, 0))
            self.assertNotEqual(slot.start.time(), time(15, 30))

if __name__ == "__main__":
    unittest.main()
