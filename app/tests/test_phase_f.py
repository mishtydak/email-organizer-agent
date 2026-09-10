import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dashboard_service import DashboardService
from review_queue import ReviewState
from task_manager import Task
import pytest
from audit import AUDIT_LOG

@pytest.fixture(autouse=True)
def reset_audit():
    # Clear audit log before each test
    AUDIT_LOG.clear()
    yield

def test_f1_triage_inbox():
    # F1: real/supplied triaged email appears correctly
    service = DashboardService()
    service.process_inbox()
    
    state = service.get_state()
    assert state["has_processed"] is True
    assert len(state["inbox"]) > 0
    # verify the properties expected
    assert "sender" in state["inbox"][0]
    assert "priority" in state["inbox"][0]

def test_f2_draft_queue():
    # F2: draft appears, edit works, approval works, rejection works, unapproved send remains blocked
    service = DashboardService()
    service.process_inbox()
    
    # Draft appears
    state = service.get_state()
    drafts = state["drafts"]
    assert len(drafts) > 0
    draft_id = drafts[0]["id"]
    
    # Edit works
    service.edit_draft(draft_id, "New Subject", "New Body")
    updated_state = service.get_state()
    updated_draft = next(d for d in updated_state["drafts"] if d["id"] == draft_id)
    assert updated_draft["subject"] == "New Subject"
    assert updated_draft["body"] == "New Body"
    
    # Unapproved send remains blocked
    with pytest.raises(PermissionError):
        service.send_draft(draft_id)
        
    # Approval works
    service.approve_draft(draft_id, "Test Reviewer")
    approved_draft = next(d for d in service.get_state()["drafts"] if d["id"] == draft_id)
    assert approved_draft["state"] == ReviewState.APPROVED.value
    
    # Rejection works
    draft_id_2 = drafts[1]["id"]
    service.reject_draft(draft_id_2, "Test Reviewer")
    rejected_draft = next(d for d in service.get_state()["drafts"] if d["id"] == draft_id_2)
    assert rejected_draft["state"] == ReviewState.REJECTED.value

def test_f3_action_items():
    # F3: task appears, unconfirmed completion remains pending, confirmed completion becomes completed
    service = DashboardService()
    # Mocking task extraction by manually inserting one
    from task_manager import create_task
    task = create_task("Test task", "2026-10-10", "student")
    task.id = "task-1"
    service.tasks[task.id] = task
    
    # Unconfirmed completion remains pending
    service.complete_task("task-1", confirmed=False)
    assert service.tasks["task-1"].status == "pending"
    
    # Confirmed completion becomes completed
    service.complete_task("task-1", confirmed=True)
    assert service.tasks["task-1"].status == "completed"

def test_f4_meeting_requests():
    # F4: meeting request appears, available slots can be displayed, confirmation without approval is rejected
    service = DashboardService()
    # Mock meeting
    from meeting_agent import MeetingRequest
    req = MeetingRequest(True, "Monday", "10 am", "Meeting")
    req.id = "meet-1"
    req.available_slots = ["Slot 1"]
    req.status = "pending"
    service.meetings[req.id] = req
    
    # Confirmation without approval is rejected
    with pytest.raises(PermissionError):
        service.confirm_meeting("meet-1", "Slot 1", approved=False)
        
    # Confirmation works
    service.confirm_meeting("meet-1", "Slot 1", approved=True)
    assert service.meetings["meet-1"].status == "approved"

def test_f5_follow_ups():
    # F5: follow-up appears, due status is calculated correctly
    service = DashboardService()
    from followup_agent import FollowUp
    from datetime import datetime, timedelta
    
    f = FollowUp("Test email", datetime.now() - timedelta(days=1))
    f.id = "f-1"
    service.follow_ups.append(f)
    
    state = service.get_state()
    f_dto = state["follow_ups"][0]
    assert f_dto["is_due"] is True

def test_f6_audit_history():
    # F6: approval/rejection/edit actions appear in audit history
    service = DashboardService()
    service.process_inbox()
    
    draft_id = list(service.drafts.keys())[0]
    service.approve_draft(draft_id, "Reviewer 1")
    
    state = service.get_state()
    audit_log = state["audit_log"]
    
    actions = [a["action"] for a in audit_log]
    assert "create_draft" in actions
    assert "approve_email" in actions

def test_f7_metrics():
    # F7: metrics are calculated from actual records
    service = DashboardService()
    service.process_inbox()
    
    draft_id = list(service.drafts.keys())[0]
    service.approve_draft(draft_id, "Reviewer 1")
    
    state = service.get_state()
    metrics = state["metrics"]
    
    assert metrics["approved_count"] >= 1
    assert metrics["total_drafts_reviewed"] >= 1
    assert metrics["average_review_time_seconds"] == "N/A" or "s" in str(metrics["average_review_time_seconds"])
