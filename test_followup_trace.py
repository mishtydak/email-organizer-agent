import sys
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.append('app')

from dashboard_service import DashboardService
from task_manager import get_due_follow_ups
from classifier import EmailClassification

class MockEmail:
    def __init__(self, subject, body, sender="researcher@example.com"):
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
        subject="Research Paper Review",
        body="Hi,\n\nPlease review the research paper and get back to me in 2 days.\n\nRegards,\nResearcher"
    )
    service.gmail_connector = MockGmailConnector(email)
    
    # Mocking classification to return High priority so a follow-up is created
    mock_classification = EmailClassification(
        sender_category="Collaborator",
        email_type="Request",
        priority="High"
    )
    
    with patch('dashboard_service.classify_email_safe', return_value=mock_classification):
        print("--- Tracing Follow-up Creation ---")
        service.process_inbox()
        
    print("\n--- Checking Pipeline ---")
    print(f"Follow-ups created: {len(service.follow_ups)}")
    if service.follow_ups:
        fu = service.follow_ups[0]
        print(f"FollowUp object: {fu.email_subject} - Reminder: {fu.reminder_at} - Status: {fu.status}")
    else:
        print("No follow-up was created. Let's check classification.")
        print(f"Inbox item priority: {service.inbox[0]['priority']}")
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
