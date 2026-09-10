import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from dashboard_service import DashboardService
from gmail_connector import Email
from models import Email

def run_test():
    print("Running End-to-End Meeting Test with Mocked Calendar...")
    
    # Simulate an incoming email
    test_email = Email(
        message_id="test-email-id",
        thread_id="test-thread-id",
        sender="student@example.com",
        subject="Research Meeting Discussion",
        body="Hi,\n\nCan we schedule a meeting on Friday at 3 pm to discuss the research project?\n\nRegards,\nStudent"
    )
    
    with patch('dashboard_service.GmailConnector.fetch_emails', return_value=[test_email]):
        with patch('dashboard_service.GmailConnector.get_thread_messages', return_value=[]):
            
            # We want to mock GoogleCalendarConnector in dashboard_service.py so that it always returns BUSY for Friday 3pm-4pm
            with patch('dashboard_service.GoogleCalendarConnector') as MockConnectorClass:
                mock_connector = MagicMock()
                # Find the date of the next Friday
                today = datetime.now()
                days_ahead = 4 - today.weekday() # Friday is 4
                if days_ahead <= 0: days_ahead += 7
                next_friday = (today.date().replace(day=today.day) + type(today.date() - today.date())(days=days_ahead))
                
                # Mock get_busy_periods to return busy from 15:00 to 16:00 UTC on next Friday
                # (Note that calendar_agent converts Z to local timezone, so we should make it absolute UTC matching local 3pm if possible,
                # but to simplify, we can just assume local time = UTC for the mock)
                next_friday_str = next_friday.isoformat()
                
                mock_connector.get_busy_periods.return_value = [
                    {
                        "start": f"{next_friday_str}T15:00:00Z",
                        "end": f"{next_friday_str}T16:00:00Z"
                    }
                ]
                MockConnectorClass.return_value = mock_connector
            
                service = DashboardService()
                
                # Because we mocked the class AFTER __init__ logic in some ways, wait DashboardService __init__ is called here!
                # Actually DashboardService__init__ will try to instantiate GoogleCalendarConnector which returns mock_connector.
                
                service.process_inbox()
                
                state = service.get_state()
                meetings = state["meetings"]
                
                print(f"Meetings detected: {len(meetings)}")
                if meetings:
                    meeting = meetings[0]
                    print(f"Meeting Requested: {meeting.get('status')}")
                    print(f"Proposed Date: {meeting.get('proposed_date')}")
                    print(f"Proposed Time: {meeting.get('proposed_time')}")
                    print(f"Requested Slot Status: {meeting.get('requested_slot_status')}")
                    print(f"Available Slots ({len(meeting.get('available_slots', []))}):")
                    for slot in meeting.get('available_slots', []):
                        print(f" - {slot}")
                
if __name__ == "__main__":
    run_test()
