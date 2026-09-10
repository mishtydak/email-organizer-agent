import sys
import os
from unittest.mock import patch
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from dashboard_service import DashboardService
from gmail_connector import Email

def run_test():
    print("Running End-to-End Meeting Test...")
    
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
            service = DashboardService()
            
            print(f"Calendar Status: {service.diagnostics['calendar_status']}")
            
            service.process_inbox()
            
            state = service.get_state()
            meetings = state["meetings"]
            
            print(f"Meetings detected: {len(meetings)}")
            if meetings:
                meeting = meetings[0]
                print(f"Meeting Requested: {meeting.get('status')}")
                print(f"Proposed Date: {meeting.get('proposed_date')}")
                print(f"Proposed Time: {meeting.get('proposed_time')}")
                print(f"Available Slots ({len(meeting.get('available_slots', []))}):")
                for slot in meeting.get('available_slots', []):
                    print(f" - {slot}")
                
if __name__ == "__main__":
    run_test()
