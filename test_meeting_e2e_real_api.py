import sys
import os
from unittest.mock import patch
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from dashboard_service import DashboardService
from calendar_connector import GoogleCalendarConnector
from models import Email

LOCAL_TZ = ZoneInfo("Asia/Kolkata")

def run_test():
    print("Running Real API Timezone Test...")
    
    # Let's first directly query the real calendar connector and print UTC vs IST
    connector = GoogleCalendarConnector()
    
    # We look for busy periods on the next Friday 
    today = datetime.now(LOCAL_TZ)
    days_ahead = 4 - today.weekday()
    if days_ahead <= 0: days_ahead += 7
    next_friday = (today.date().replace(day=today.day) + timedelta(days=days_ahead))
    
    time_min = datetime.combine(next_friday, time(0, 0)).replace(tzinfo=LOCAL_TZ)
    time_max = time_min + timedelta(days=1)
    
    print(f"Querying real Google Calendar from {time_min} to {time_max}...")
    
    busy_periods = connector.get_busy_periods(time_min, time_max)
    
    print(f"Real Busy Periods found: {len(busy_periods)}")
    for busy in busy_periods:
        b_start_utc = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
        b_end_utc = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))
        
        b_start_ist = b_start_utc.astimezone(LOCAL_TZ)
        b_end_ist = b_end_utc.astimezone(LOCAL_TZ)
        
        print(f" - Google Calendar: {b_start_utc.strftime('%H:%M')}–{b_end_utc.strftime('%H:%M')} UTC")
        print(f"                    {b_start_ist.strftime('%H:%M')}–{b_end_ist.strftime('%H:%M')} Asia/Kolkata")
        
    print("\nSimulating Dashboard Email Processing...")
    
    # Simulate an incoming email asking for Friday at 3 PM
    test_email = Email(
        message_id="test-email-id",
        thread_id="test-thread-id",
        sender="student@example.com",
        subject="Project Review Meeting",
        body="Hi,\n\nCan we schedule a meeting on Friday at 3 pm for the Project Review?\n\nRegards,\nStudent"
    )
    
    with patch('dashboard_service.GmailConnector.fetch_emails', return_value=[test_email]):
        with patch('dashboard_service.GmailConnector.get_thread_messages', return_value=[]):
            
            service = DashboardService()
            service.process_inbox()
            
            state = service.get_state()
            meetings = state["meetings"]
            
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
