import sys
import uuid
import json
from datetime import datetime, timedelta
sys.path.append('app')

from dashboard_service import DashboardService
from task_manager import get_due_follow_ups

class MockEmail:
    def __init__(self, subject, body, sender="student@example.com"):
        self.id = str(uuid.uuid4())
        self.thread_id = self.id
        self.subject = subject
        self.body = body
        self.sender = sender

class MockGmailConnector:
    def __init__(self, email):
        self.email = email
    
    def fetch_emails(self, max_results=5):
        return [self.email]
    
    def get_thread_messages(self, thread_id):
        return []

def main():
    service = DashboardService()
    
    email = MockEmail(
        subject="Research Paper Review \u2013 Follow-up Required",
        body="Dear Professor,\n\nI have shared the updated research paper for your review.\n\nCould you please review it and get back to me in 2 days with your feedback?\nI would like to make the necessary changes based on your suggestions.\n\nThank you.\nRegards,\nStudent"
    )
    service.gmail_connector = MockGmailConnector(email)
    
    print("--- Tracing Follow-up Creation (with real Groq classification) ---")
    service.process_inbox()
    
    print("\n--- Checking Pipeline ---")
    print(f"Follow-ups created: {len(service.follow_ups)}")
    if service.follow_ups:
        fu = service.follow_ups[0]
        print(f"FollowUp object: {fu.email_subject} - Reminder: {fu.reminder_at} - Status: {fu.status}")
    else:
        print("No follow-up was created. Classification failed to trigger it.")
        print(f"Inbox item priority: {service.inbox[0].get('priority')}")
        print(f"Inbox item email_type: {service.inbox[0].get('email_type')}")
        print(f"Inbox item action_items: {len(service.inbox[0].get('action_items', []))}")
        return
        
    print("\n--- Checking Retrieval (get_due_follow_ups) ---")
    due_now = get_due_follow_ups(service.follow_ups)
    print(f"Due now: {len(due_now)}")
    
    # Simulate time passing by modifying reminder_at
    fu.reminder_at = datetime.now() - timedelta(minutes=1)
    
    due_later = get_due_follow_ups(service.follow_ups)
    print(f"Due after simulating time passing: {len(due_later)}")
    if due_later:
        print(f"Returned object: {due_later[0].email_subject}")
        
    print("\n--- Checking Dashboard Display State ---")
    state = service.get_state()
    fu_state = state["follow_ups"]
    print(f"Follow-ups in dashboard state: {len(fu_state)}")
    if fu_state:
        print(f"Is due in dashboard: {fu_state[0]['is_due']}")
        
if __name__ == '__main__':
    main()
