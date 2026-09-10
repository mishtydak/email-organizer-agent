import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from classifier import classify_email, extract_action_items, classify_email_safe
from models import Email
from dashboard_service import DashboardService

def run_isolated_test():
    print("==================================================")
    print("ISOLATED GEMINI TEST")
    print("==================================================")
    
    mock_email = Email(
        message_id="mock-1",
        thread_id="mock-thread-1",
        sender="student@example.com",
        subject="Project Extension Request",
        body="I am a student and I need a two-day extension for my project submission."
    )
    
    try:
        classification = classify_email(mock_email)
        print("classification output:")
        print(classification.model_dump_json(indent=2))
    except Exception as e:
        print(f"classify_email failed: {type(e).__name__}: {e}")
        
    try:
        extraction = extract_action_items(mock_email)
        print("extraction output:")
        print(extraction.model_dump_json(indent=2))
    except Exception as e:
        print(f"extract_action_items failed: {type(e).__name__}: {e}")

def run_real_gmail_test():
    print("\n==================================================")
    print("REAL GMAIL TEST (MOCKING GMAIL CONNECTOR WITH SAME EMAIL)")
    print("==================================================")
    
    # We use a mock email simulating what Gmail would return
    mock_email = Email(
        message_id="mock-2",
        thread_id="mock-thread-2",
        sender="student@example.com",
        subject="Project Extension Request",
        body="I am a student and I need a two-day extension for my project submission."
    )
    
    print(f"Email:\n{mock_email.subject}\n")
    
    classification = classify_email_safe(mock_email)
    print("Classification:")
    print(f"Sender category: {classification.sender_category}")
    print(f"Email type: {classification.email_type}")
    print(f"Priority: {classification.priority}")
    if hasattr(classification, "last_error") and classification.last_error:
        print(f"Last Error: {classification.last_error}")
        
    print("\nVerifying Dashboard propagation...")
    
    with patch('dashboard_service.GmailConnector.fetch_emails', return_value=[mock_email]):
        with patch('dashboard_service.GmailConnector.get_thread_messages', return_value=[]):
            service = DashboardService()
            service.process_inbox()
            
            state = service.get_state()
            inbox = state["inbox"]
            
            if inbox:
                item = inbox[0]
                print(f"Dashboard received Sender category: {item.get('sender_category')}")
                print(f"Dashboard received Email type: {item.get('email_type')}")
                print(f"Dashboard received Priority: {item.get('priority')}")
                
                if item.get('sender_category') != "Unknown":
                    print("\nSUCCESS: Values correctly reached the dashboard!")
                else:
                    print("\nFAILED: Dashboard still shows Unknown.")

if __name__ == "__main__":
    run_isolated_test()
    run_real_gmail_test()
