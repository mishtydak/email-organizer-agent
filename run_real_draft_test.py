import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from dashboard_service import DashboardService
from review_queue import ReviewState

def run_real_test():
    print("==================================================")
    print("CONTROLLED REAL EMAIL TEST")
    print("==================================================")
    
    # 1. Initialize service and connectors
    service = DashboardService()
    
    if not getattr(service.gmail_connector, 'service', None):
        print("FAIL: Gmail Connector not fully authenticated or service not initialized.")
        return
        
    print("Gmail Connector initialized. Fetching inbox...")
    
    # 2. Process inbox to generate a draft
    service.process_inbox()
    state = service.get_state()
    
    drafts = state["drafts"]
    if not drafts:
        print("No drafts were created. Please ensure there is a recent email in the inbox that requires a reply.")
        return
        
    # We will pick the most recent draft
    target_draft = drafts[0]
    draft_id = target_draft["id"]
    
    print(f"Selected Draft ID: {draft_id}")
    print(f"Recipient: {target_draft['recipient']}")
    print(f"Original Subject: {target_draft['subject']}")
    print(f"Original Body:\n{target_draft['body']}")
    
    # 3. Edit Draft
    print("\n--- Editing Draft ---")
    new_body = target_draft['body'] + "\n\n[Edited dynamically by test script]"
    service.edit_draft(draft_id, target_draft['subject'], new_body)
    
    # Fetch updated draft
    updated_draft = service.drafts[draft_id]
    print(f"State after edit: {updated_draft.state.value}")
    print(f"Version after edit: {updated_draft.version}")
    
    # 4. Approve Draft
    print("\n--- Approving Draft ---")
    service.approve_draft(draft_id, "Automated Test Runner")
    print(f"State after approval: {updated_draft.state.value}")
    
    # 5. Send Draft
    print("\n--- Sending Draft ---")
    try:
        service.send_draft(draft_id)
        print(f"State after send: {updated_draft.state.value}")
        print("\nSUCCESS: Real email sent and pipeline validated!")
    except Exception as e:
        print(f"\nFAIL: Failed to send real email. Error: {e}")
        print(f"State remains: {updated_draft.state.value}")

if __name__ == "__main__":
    run_real_test()
