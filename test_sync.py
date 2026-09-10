import sys
import uuid
from datetime import datetime, timedelta
sys.path.append('app')

from dashboard_service import DashboardService
from classifier import EmailClassification

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
        subject="Please review the updated research paper and get back to me in 2 days.",
        body="Dear Professor,\n\nI have shared the updated research paper for your review.\n\nCould you please review it and get back to me in 2 days with your feedback?\nI would like to make the necessary changes based on your suggestions.\n\nThank you.\nRegards,\nStudent"
    )
    service.gmail_connector = MockGmailConnector(email)
    
    print("--- 1. Processing Inbox ---")
    service.process_inbox()
    
    print("\n--- 2. Checking Initial State ---")
    tasks = list(service.tasks.values())
    followups = service.follow_ups
    
    print(f"Tasks: {len(tasks)}")
    if tasks:
        print(f"Task 1 status: {tasks[0].status}")
        
    print(f"FollowUps: {len(followups)}")
    if followups:
        print(f"FollowUp 1 status: {followups[0].status}")
        
    # Check if they show up in get_state
    state = service.get_state()
    print(f"FollowUps in dashboard state: {len(state['follow_ups'])}")
    
    print("\n--- 3. Simulating 'Complete Task' ---")
    if tasks:
        service.complete_task(tasks[0].id)
        print("Task marked completed.")
        
    print("\n--- 4. Checking Post-Completion State ---")
    print(f"Task 1 status: {tasks[0].status}")
    print(f"FollowUp 1 status: {followups[0].status}")
    
    state2 = service.get_state()
    print(f"FollowUps in dashboard state: {len(state2['follow_ups'])}")
    
    print("\n--- 5. Checking Audit Log ---")
    for log in state2["audit_log"]:
        print(f"Audit: {log['action']} - {log['actor']}")

if __name__ == '__main__':
    main()
