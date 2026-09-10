import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from review_queue import ReviewState, create_review_item, edit_review_item, approve_review_item, reject_review_item, mark_as_sent
from dashboard_service import DashboardService
from gmail_sender import send_approved_email

class TestDraftWorkflow(unittest.TestCase):

    def setUp(self):
        self.service = DashboardService()
        self.service.gmail_connector = MagicMock()
        self.service.gmail_connector.service = MagicMock()

    def test_1_create_draft(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        self.assertEqual(draft.state, ReviewState.DRAFT)
        self.assertEqual(getattr(draft, 'version', 1), 1)

    def test_2_edit_draft(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        draft.version = 1
        self.service.drafts["mock-id"] = draft
        
        self.service.edit_draft("mock-id", "New Subject", "New Body")
        
        self.assertEqual(draft.state, ReviewState.DRAFT)
        self.assertEqual(draft.subject, "New Subject")
        self.assertEqual(draft.body, "New Body")
        self.assertEqual(draft.version, 2)

    def test_3_send_draft_fails(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        self.service.drafts["mock-id"] = draft
        
        with self.assertRaises(PermissionError):
            self.service.send_draft("mock-id")
            
        self.assertEqual(draft.state, ReviewState.DRAFT)

    def test_4_approve_draft(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        self.service.drafts["mock-id"] = draft
        
        self.service.approve_draft("mock-id", "Faculty User")
        
        self.assertEqual(draft.state, ReviewState.APPROVED)
        self.assertEqual(draft.reviewer, "Faculty User")

    def test_5_send_approved_draft(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        self.service.drafts["mock-id"] = draft
        self.service.approve_draft("mock-id", "Faculty User")
        
        self.service.send_draft("mock-id")
        
        self.assertEqual(draft.state, ReviewState.SENT)

    def test_6_reject_draft(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        self.service.drafts["mock-id"] = draft
        
        self.service.reject_draft("mock-id", "Faculty User")
        
        self.assertEqual(draft.state, ReviewState.REJECTED)

    def test_7_send_rejected_draft_fails(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        self.service.drafts["mock-id"] = draft
        self.service.reject_draft("mock-id", "Faculty User")
        
        with self.assertRaises(PermissionError):
            self.service.send_draft("mock-id")
            
        self.assertEqual(draft.state, ReviewState.REJECTED)

    def test_8_send_failure_keeps_approved(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        self.service.drafts["mock-id"] = draft
        self.service.approve_draft("mock-id", "Faculty User")
        
        # Mock the Gmail API call to fail
        self.service.gmail_connector.service.users().messages().send.side_effect = Exception("Gmail API Error")
        
        with self.assertRaises(Exception):
            self.service.send_draft("mock-id")
            
        # The state MUST remain APPROVED, not SENT!
        self.assertEqual(draft.state, ReviewState.APPROVED)

    def test_9_repeated_send_fails(self):
        draft = create_review_item("test@example.com", "Test Subject", "Test Body")
        self.service.drafts["mock-id"] = draft
        self.service.approve_draft("mock-id", "Faculty User")
        
        # First send succeeds
        self.service.send_draft("mock-id")
        self.assertEqual(draft.state, ReviewState.SENT)
        
        # Second send fails
        with self.assertRaises(PermissionError):
            self.service.send_draft("mock-id")

    def test_10_audit_contains_actions(self):
        from audit import get_audit_log, log_action
        
        # We don't want to interfere with other tests or global state, but let's check recent logs
        draft = create_review_item("audit@example.com", "Subject", "Body")
        draft.version = 1
        self.service.drafts["mock-audit"] = draft
        
        self.service.edit_draft("mock-audit", "Subject", "Body Edited")
        self.service.approve_draft("mock-audit", "Faculty")
        self.service.send_draft("mock-audit")
        
        logs = get_audit_log()
        actions = [log.action for log in logs[-4:]]
        
        self.assertIn("create_draft", actions)
        self.assertIn("edit_draft", actions)
        self.assertIn("approve_email", actions)
        self.assertIn("send_email", actions)

if __name__ == '__main__':
    unittest.main()
