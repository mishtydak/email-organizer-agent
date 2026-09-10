import os
import uuid
from datetime import datetime, timedelta

from review_queue import (
    create_review_item,
    edit_review_item,
    approve_review_item,
    reject_review_item,
    ReviewState
)
from task_manager import create_task, mark_task_complete, schedule_follow_up
from meeting_agent import extract_meeting_request, confirm_meeting, get_meeting_proposals
from audit import get_audit_log, log_action
from gmail_connector import GmailConnector
from gmail_sender import send_approved_email
from thread_grounding import ground_email_from_thread
from draft_agent import draft_reply
from classifier import (
    classify_email_safe, 
    extract_action_items_safe,
    FallbackEmailClassification,
    FallbackActionExtraction
)
from calendar_agent import propose_meeting_slots
from calendar_connector import GoogleCalendarConnector, TOKEN_FILE


class DashboardService:
    def __init__(self):
        self.inbox = []
        self.drafts = {}
        self.tasks = {}
        self.meetings = {}
        self.follow_ups = []
        
        self.gmail_connector = None
        self.gmail_sender = None
        self.has_processed = False
        
        self.pipeline_status = {
            "Gmail Ingestion": "PENDING",
            "AI Classification": "PENDING",
            "Action Extraction": "PENDING",
            "Thread Grounding": "PENDING",
            "Draft Generation": "PENDING",
            "Faculty Review": "PENDING",
            "Audit Logging": "PENDING"
        }
        
        self.diagnostics = {
            "gmail_status": "Disconnected",
            "groq_status": "Idle",
            "groq_error": None,
            "calendar_status": "Not configured",
            "thread_grounding": "Active",
            "auto_send": "DISABLED",
            "last_run": None,
            "emails_processed": 0
        }

        try:
            self.gmail_connector = GmailConnector()
            self.gmail_sender = send_approved_email
            self.diagnostics["gmail_status"] = "Connected"
        except Exception as e:
            print("Gmail connector not initialized:", e)
            self.diagnostics["gmail_status"] = "Disconnected"

        self.calendar_connector = None
        try:
            if not os.path.exists(TOKEN_FILE):
                self.diagnostics["calendar_status"] = "Authentication required"
            else:
                self.calendar_connector = GoogleCalendarConnector()
                try:
                    now = datetime.now()
                    self.calendar_connector.get_busy_periods(now, now + timedelta(days=1))
                    self.diagnostics["calendar_status"] = "Connected"
                except Exception as e:
                    print(f"Calendar API error: {e}")
                    self.diagnostics["calendar_status"] = "Error"
        except Exception as e:
            print("Calendar connector not initialized:", e)
            self.diagnostics["calendar_status"] = "Error"

    def process_inbox(self):
        print("Processing real inbox...")
        self.diagnostics["last_run"] = datetime.now().isoformat()
        self.has_processed = True
        self.inbox = []

        # 1. Gmail Ingestion
        emails = []
        if self.gmail_connector:
            try:
                emails = self.gmail_connector.fetch_emails(max_results=5)
                self.pipeline_status["Gmail Ingestion"] = "✓"
                self.diagnostics["emails_processed"] = len(emails)
            except Exception as e:
                print("Failed to fetch emails:", e)
                self.pipeline_status["Gmail Ingestion"] = "FAILED"
        else:
            self.pipeline_status["Gmail Ingestion"] = "FAILED"
            
        if not emails:
            return

        fallback_used_in_classification = False
        fallback_used_in_extraction = False
        any_grounded = False

        for email in emails:
            draft_dict = {
                "id": str(uuid.uuid4()),
                "sender": email.sender,
                "subject": email.subject,
                "body": email.body,
                "priority": "Low",
                "action_items": [],
                "evidence": [],
                "ai_source": "groq"
            }
            
            # 2. AI Classification
            try:
                classification = classify_email_safe(email)
                draft_dict["sender_category"] = classification.sender_category
                draft_dict["email_type"] = classification.email_type
                draft_dict["priority"] = classification.priority
                
                if isinstance(classification, FallbackEmailClassification):
                    fallback_used_in_classification = True
                    if hasattr(classification, "last_error") and classification.last_error:
                        self.diagnostics["groq_error"] = str(classification.last_error)
            except Exception as e:
                print(f"Critial classification crash: {e}")
                draft_dict["sender_category"] = "Unknown"
                draft_dict["email_type"] = "Unknown"
                draft_dict["priority"] = "Low"
                fallback_used_in_classification = True

            # 3. Action Extraction
            try:
                extraction = extract_action_items_safe(email)
                # Ensure action_items are dictionaries when sent to frontend
                action_items_list = []
                for a in extraction.action_items:
                    # if a is an object (ActionItem), convert it to dict, otherwise if already dict, leave it
                    action_items_list.append(a.model_dump() if hasattr(a, "model_dump") else a)
                draft_dict["action_items"] = action_items_list
                
                if isinstance(extraction, FallbackActionExtraction):
                    fallback_used_in_extraction = True
                    if hasattr(extraction, "last_error") and extraction.last_error:
                        self.diagnostics["groq_error"] = str(extraction.last_error)
            except Exception as e:
                print(f"Critical extraction crash: {e}")
                fallback_used_in_extraction = True

            # 4. Thread Grounding
            draft_dict["evidence"] = []
            if self.gmail_connector and email.thread_id:
                try:
                    raw_messages = self.gmail_connector.get_thread_messages(email.thread_id)
                    grounding_result = ground_email_from_thread(email, raw_messages)
                    if grounding_result["status"] == "grounded":
                        # Grounding_result["evidence"] contains Evidence objects. Convert to dicts for frontend.
                        evidence_list = []
                        for ev in grounding_result.get("evidence", []):
                            if hasattr(ev, "__dict__"):
                                evidence_list.append(ev.__dict__)
                            else:
                                evidence_list.append(ev)
                        draft_dict["evidence"] = evidence_list
                        any_grounded = True
                except Exception as e:
                    print("Error during thread grounding:", e)

            # 5. Draft Generation
            draft_response = draft_reply(email)
            body_draft = draft_response.get("body")
            draft_source = draft_response.get("template", "AI Generated")
            
            if not body_draft:
                # Basic fallback
                body_draft = "Thank you for your email."
                draft_source = "Fallback"
                if draft_dict["action_items"]:
                    actions_text = ", ".join(
                        a.description if hasattr(a, 'description') else a['description'] 
                        for a in draft_dict["action_items"]
                    )
                    body_draft = f"Thank you for your email. I have noted the following actions: {actions_text}"
            
            draft_dict["draft_source"] = draft_source

            # 6. Create Review Item
            review_item = create_review_item(
                recipient=draft_dict["sender"],
                subject=f"Re: {draft_dict['subject']}",
                body=body_draft
            )
            review_item.version = 1 
            self.drafts[draft_dict["id"]] = review_item
            
            self.inbox.append(draft_dict)

            # 7. Create Tasks
            for action in draft_dict["action_items"]:
                task = create_task(
                    description=action.get('description', ''),
                    deadline=action.get('deadline', ''),
                    assigned_to=action.get('assigned_to', ''),
                    confidence=action.get('confidence', None)
                )
                task_id = str(uuid.uuid4())
                task.source_email = draft_dict["subject"]
                task.source_id = draft_dict["id"]
                task.id = task_id
                self.tasks[task_id] = task

            # 8. Detect Meetings
            meeting_req = extract_meeting_request(email)
            if meeting_req.meeting_requested:
                meeting_req.id = str(uuid.uuid4())
                meeting_req.sender = draft_dict["sender"]
                meeting_req.subject = draft_dict["subject"]
                meeting_req.available_slots = []
                meeting_req.status = "pending"
                
                if self.calendar_connector:
                    try:
                        start_date = datetime.now()
                        result = get_meeting_proposals(
                            meeting_req,
                            self.calendar_connector,
                            start_date=start_date.date(),
                            days=7
                        )
                        
                        if isinstance(result, tuple) and len(result) == 2:
                            proposals, requested_status = result
                        else:
                            proposals = result
                            requested_status = None
                            
                        meeting_req.requested_slot_status = requested_status
                        
                        formatted_slots = []
                        for i, p in enumerate(proposals):
                            slot_str = p.start.strftime("%Y-%m-%d %I:%M %p")
                            if i == 0 and requested_status == "AVAILABLE":
                                slot_str += " — AVAILABLE"
                            formatted_slots.append(slot_str)
                            
                        meeting_req.available_slots = formatted_slots
                    except Exception as e:
                        print("Failed to propose meeting slots:", e)
                    
                self.meetings[meeting_req.id] = meeting_req

            # 9. Follow-ups
            requires_follow_up = False
            
            if draft_dict["priority"] in ["Critical", "High"]:
                requires_follow_up = True
            elif draft_dict.get("email_type") in ["Request", "Deadline"]:
                requires_follow_up = True
            elif draft_dict.get("action_items") and len(draft_dict["action_items"]) > 0:
                requires_follow_up = True
                
            if requires_follow_up:
                follow_up = schedule_follow_up(email, days=2)
                follow_up.id = str(uuid.uuid4())
                follow_up.source_id = draft_dict["id"]
                self.follow_ups.append(follow_up)

        # Update Pipeline Statuses
        self.pipeline_status["AI Classification"] = "FALLBACK" if fallback_used_in_classification else "✓"
        self.pipeline_status["Action Extraction"] = "FALLBACK" if fallback_used_in_extraction else "✓"
        self.pipeline_status["Thread Grounding"] = "✓" if any_grounded else "REJECTED / NO EVIDENCE"
        self.pipeline_status["Draft Generation"] = "✓" if emails else "FAILED"
        self.pipeline_status["Faculty Review"] = "PENDING_REVIEW" if emails else "PENDING"
        self.pipeline_status["Audit Logging"] = "✓" if emails else "PENDING"

        # Update Diagnostics
        if fallback_used_in_classification or fallback_used_in_extraction:
            self.diagnostics["groq_status"] = "Fallback"
        else:
            self.diagnostics["groq_status"] = "Connected"

    def get_state(self):
        drafts_list = []
        for d_id, d in self.drafts.items():
            # Match the source from inbox if possible
            draft_source = "AI Generated"
            for item in self.inbox:
                if item["sender"] == d.recipient:
                    draft_source = item.get("draft_source", "AI Generated")
                    break
            
            drafts_list.append({
                "id": d_id,
                "recipient": d.recipient,
                "subject": d.subject,
                "body": d.body,
                "state": d.state.value,
                "reviewer": d.reviewer,
                "version": getattr(d, 'version', 1),
                "source": draft_source
            })
            
        tasks_list = []
        for t_id, t in self.tasks.items():
            tasks_list.append({
                "id": t_id,
                "description": t.description,
                "deadline": t.deadline,
                "assigned_to": t.assigned_to,
                "confidence": getattr(t, 'confidence', None),
                "status": t.status,
                "source_email": getattr(t, 'source_email', '')
            })
            
        meetings_list = []
        for m_id, m in self.meetings.items():
            meetings_list.append({
                "id": m_id,
                "sender": getattr(m, 'sender', ''),
                "subject": getattr(m, 'subject', m.purpose),
                "proposed_date": m.proposed_date,
                "proposed_time": m.proposed_time,
                "requested_slot_status": getattr(m, 'requested_slot_status', None),
                "available_slots": getattr(m, 'available_slots', []),
                "status": getattr(m, 'status', 'pending')
            })
            
        followups_list = []
        now = datetime.now()
        for f in self.follow_ups:
            if getattr(f, 'status', 'pending') == 'completed':
                continue
            is_due = f.reminder_at <= now
            followups_list.append({
                "id": f.id,
                "email_subject": f.email_subject,
                "reminder_at": f.reminder_at.isoformat(),
                "status": f.status,
                "is_due": is_due
            })

        audit_log = []
        for entry in get_audit_log():
            audit_log.append({
                "action": entry.action,
                "actor": entry.actor,
                "recipient": entry.recipient,
                "subject": entry.subject,
                "timestamp": entry.timestamp.isoformat()
            })

        # Calculate Metrics F7
        audit_entries = get_audit_log()
        
        review_times = []
        draft_creation_times = {}
        for entry in audit_entries:
            key = f"{entry.recipient}-{entry.subject}"
            if entry.action == "create_draft":
                draft_creation_times[key] = entry.timestamp
            elif entry.action in ["approve_email", "reject_email"] and key in draft_creation_times:
                diff = (entry.timestamp - draft_creation_times[key]).total_seconds()
                review_times.append(diff)
                
        avg_review = sum(review_times) / len(review_times) if review_times else 0
        avg_review_display = f"{round(avg_review, 2)}s" if review_times else "N/A"
        
        metrics = {
            "total_drafts_reviewed": sum(1 for e in audit_entries if e.action in ["approve_email", "reject_email"]),
            "approved_count": sum(1 for e in audit_entries if e.action == "approve_email"),
            "rejected_count": sum(1 for e in audit_entries if e.action == "reject_email"),
            "pending_review_count": sum(1 for d in self.drafts.values() if d.state == ReviewState.DRAFT),
            "follow_up_completion_rate": 0,
            "average_review_time_seconds": avg_review_display
        }
        
        completed_follow_ups = sum(1 for f in self.follow_ups if f.status == "completed")
        if len(self.follow_ups) > 0:
            metrics["follow_up_completion_rate"] = round((completed_follow_ups / len(self.follow_ups)) * 100, 2)
            
        self.diagnostics["pending_approvals"] = metrics["pending_review_count"]

        return {
            "inbox": self.inbox,
            "drafts": drafts_list,
            "tasks": tasks_list,
            "meetings": meetings_list,
            "follow_ups": followups_list,
            "audit_log": audit_log,
            "metrics": metrics,
            "pipeline_status": self.pipeline_status,
            "diagnostics": self.diagnostics,
            "has_processed": self.has_processed
        }

    def edit_draft(self, draft_id, subject, body):
        item = self.drafts[draft_id]
        edit_review_item(item, subject=subject, body=body)
        return True

    def approve_draft(self, draft_id, reviewer):
        item = self.drafts[draft_id]
        approve_review_item(item, reviewer)
        return True

    def reject_draft(self, draft_id, reviewer):
        item = self.drafts[draft_id]
        reject_review_item(item, reviewer)
        return True

    def send_draft(self, draft_id):
        item = self.drafts[draft_id]
        if item.state != ReviewState.APPROVED:
            raise PermissionError("Must be approved before sending.")
            
        if self.gmail_connector and getattr(self.gmail_connector, 'service', None):
            from gmail_sender import GmailSender, send_approved_email
            
            sender = GmailSender(self.gmail_connector.service)
            # This will raise exceptions if the send fails, keeping the state as APPROVED
            send_approved_email(item, sender)
        else:
            # Fallback for mocked environments without a real service
            from review_queue import mark_as_sent
            mark_as_sent(item)
            
        return True

    def complete_task(self, task_id, confirmed=True):
        task = self.tasks[task_id]
        mark_task_complete(task, confirmed=confirmed)
        
        log_action("complete_task", "User", None, task.description)
        
        source_id = getattr(task, 'source_id', None)
        if source_id:
            for fu in self.follow_ups:
                if getattr(fu, 'source_id', None) == source_id and getattr(fu, 'status', 'pending') != "completed":
                    fu.status = "completed"
                    log_action("complete_followup_auto", "System", None, fu.email_subject)
        
        return True

    def complete_followup(self, followup_id, confirmed=True):
        for fu in self.follow_ups:
            if getattr(fu, 'id', None) == followup_id:
                fu.status = "completed"
                log_action("complete_followup", "User", None, fu.email_subject)
                
                source_id = getattr(fu, 'source_id', None)
                if source_id:
                    for task in self.tasks.values():
                        if getattr(task, 'source_id', None) == source_id and getattr(task, 'status', 'pending') != "completed":
                            mark_task_complete(task, confirmed=confirmed)
                            log_action("complete_task_auto", "System", None, task.description)
                break
        return True

    def confirm_meeting(self, meeting_id, selected_slot, approved=True):
        meeting = self.meetings[meeting_id]
        class DummySlot:
            def __init__(self, start, end):
                self.start = start
                self.end = end
                
        result = confirm_meeting(meeting, selected_slot=DummySlot(selected_slot, selected_slot), approved=approved)
        meeting.status = result["status"]
        return True
