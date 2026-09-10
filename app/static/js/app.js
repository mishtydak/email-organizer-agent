document.addEventListener('DOMContentLoaded', () => {
    
    const processBtn = document.getElementById('process-inbox-btn');
    const modal = document.getElementById('draft-modal');
    const cancelDraftBtn = document.getElementById('cancel-draft-btn');
    const saveDraftBtn = document.getElementById('save-draft-btn');
    
    processBtn.addEventListener('click', async () => {
        processBtn.disabled = true;
        processBtn.textContent = "Processing...";
        processBtn.classList.remove('pulse');
        
        try {
            const res = await fetch('/api/process', { method: 'POST' });
            if(res.ok) {
                await loadState();
            } else {
                alert("Failed to process inbox.");
            }
        } catch(e) {
            alert("Error: " + e.message);
        }
        
        processBtn.disabled = false;
        processBtn.textContent = "Process Inbox";
    });
    
    cancelDraftBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    saveDraftBtn.addEventListener('click', async () => {
        const id = document.getElementById('edit-draft-id').value;
        const subject = document.getElementById('edit-draft-subject').value;
        const body = document.getElementById('edit-draft-body').value;
        
        try {
            await fetch(`/api/drafts/${id}/edit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ subject, body })
            });
            modal.style.display = 'none';
            await loadState();
        } catch(e) {
            alert("Error saving draft: " + e.message);
        }
    });
    
    async function loadState() {
        try {
            const res = await fetch('/api/state');
            const state = await res.json();
            renderMetrics(state.metrics);
            renderDiagnostics(state.diagnostics);
            renderPipeline(state.pipeline_status);
            renderInbox(state.inbox);
            renderDrafts(state.drafts);
            renderTasks(state.tasks);
            renderMeetings(state.meetings);
            renderFollowUps(state.follow_ups);
            renderAuditLog(state.audit_log);
        } catch(e) {
            console.error("Failed to load state", e);
        }
    }
    
    function renderMetrics(metrics) {
        const container = document.getElementById('metrics-container');
        container.innerHTML = `
            <div class="card">
                <h3>Drafts Reviewed</h3>
                <div class="value">${metrics.total_drafts_reviewed}</div>
            </div>
            <div class="card">
                <h3>Pending Review</h3>
                <div class="value">${metrics.pending_review_count}</div>
            </div>
            <div class="card">
                <h3>Approved</h3>
                <div class="value" style="color: var(--success)">${metrics.approved_count}</div>
            </div>
            <div class="card">
                <h3>Rejected</h3>
                <div class="value" style="color: var(--danger)">${metrics.rejected_count}</div>
            </div>
            <div class="card">
                <h3>Follow-up Completion</h3>
                <div class="value">${metrics.follow_up_completion_rate}%</div>
            </div>
            <div class="card">
                <h3>Avg Review Time</h3>
                <div class="value">${metrics.average_review_time_seconds}</div>
            </div>
        `;
    }
    
    function renderDiagnostics(diagnostics) {
        const container = document.getElementById('diagnostics-list');
        if (!diagnostics) return;
        
        const groqErrorStr = diagnostics.groq_error ? `<br><span style="font-size:0.7rem; color:#f87171;">${diagnostics.groq_error.split('.')[0]}</span>` : '';
        
        container.innerHTML = `
            <div class="pipeline-item">
                <span class="pipeline-label">Gmail API</span>
                <span class="pipeline-status ${diagnostics.gmail_status === 'Connected' ? 'success' : 'failed'}">${diagnostics.gmail_status}</span>
            </div>
            <div class="pipeline-item" style="flex-direction: column; align-items: flex-start;">
                <div style="display:flex; justify-content:space-between; width:100%;">
                    <span class="pipeline-label">Groq (openai/gpt-oss-20b)</span>
                    <span class="pipeline-status ${diagnostics.groq_status === 'Connected' ? 'success' : (diagnostics.groq_status === 'Fallback' ? 'fallback' : 'pending')}">${diagnostics.groq_status}</span>
                </div>
                ${groqErrorStr}
            </div>
            <div class="pipeline-item">
                <span class="pipeline-label">Calendar API</span>
                <span class="pipeline-status pending">${diagnostics.calendar_status}</span>
            </div>
            <div class="pipeline-item">
                <span class="pipeline-label">Thread Grounding</span>
                <span class="pipeline-status success">${diagnostics.thread_grounding}</span>
            </div>
            <div class="pipeline-item">
                <span class="pipeline-label">Auto-send</span>
                <span class="pipeline-status pending">${diagnostics.auto_send}</span>
            </div>
            <div class="pipeline-item">
                <span class="pipeline-label">Pending Approvals</span>
                <span class="pipeline-status ${diagnostics.pending_approvals > 0 ? 'fallback' : 'success'}">${diagnostics.pending_approvals}</span>
            </div>
            <div class="pipeline-item">
                <span class="pipeline-label">Last Pipeline Run</span>
                <span class="pipeline-status" style="font-size: 0.8rem">${diagnostics.last_run ? new Date(diagnostics.last_run).toLocaleTimeString() : 'Never'}</span>
            </div>
        `;
    }

    function renderPipeline(pipeline) {
        const container = document.getElementById('pipeline-list');
        if (!pipeline) return;
        
        let html = '';
        for (const [step, status] of Object.entries(pipeline)) {
            let statusClass = 'pending';
            let displayStatus = status;
            if (status === '✓') {
                statusClass = 'success';
                displayStatus = '✓ SUCCESS';
            }
            if (status === 'PENDING_REVIEW') {
                statusClass = 'success';
            }
            if (status === 'FAILED' || status.includes('REJECTED')) {
                statusClass = 'failed';
            }
            if (status === 'FALLBACK') {
                statusClass = 'fallback';
                displayStatus = '⚠ FALLBACK';
            }
            
            html += `
                <div class="pipeline-item">
                    <span class="pipeline-label">${step}</span>
                    <span class="pipeline-status ${statusClass}">${displayStatus}</span>
                </div>
            `;
        }
        container.innerHTML = html;
    }
    
    function renderInbox(inbox) {
        const container = document.getElementById('inbox-list');
        if(!inbox || inbox.length === 0) {
            container.innerHTML = "<p>No emails to display.</p>";
            return;
        }
        
        container.innerHTML = inbox.map(email => `
            <div class="item-card">
                <div class="item-header">
                    <span>From: ${email.sender}</span>
                    <span class="badge ${email.priority.toLowerCase()}">${email.priority}</span>
                </div>
                <div class="item-title">${email.subject}</div>
                <div class="item-body">
                    Type: ${email.email_type} | Category: ${email.sender_category}
                    ${email.action_items && email.action_items.length ? '<br>⚡ Contains Action Items' : ''}
                </div>
                ${email.evidence && email.evidence.length > 0 ? `
                <div class="evidence-box">
                    <strong style="color:#10b981;">GROUNDING: GROUNDED</strong><br><br>
                    ${email.evidence.map(ev => `
                        <div style="margin-bottom:8px; border-left:2px solid rgba(255,255,255,0.2); padding-left:8px;">
                            <strong>Subject:</strong> ${ev.subject || 'Unknown'}<br>
                            <strong>Sender:</strong> ${ev.sender || 'Unknown'}<br>
                            <strong>Relevance:</strong> ${ev.relevance || 'N/A'}<br>
                            <strong>Content:</strong> <span style="opacity:0.8">${(ev.content || '').substring(0, 100)}...</span>
                        </div>
                    `).join('')}
                </div>
                ` : `
                <div class="evidence-box">
                    <strong style="color:#ef4444;">GROUNDING: REJECTED</strong><br>
                    Reason: No relevant prior message found.
                </div>
                `}
            </div>
        `).join('');
    }
    
    function renderDrafts(drafts) {
        const container = document.getElementById('drafts-list');
        if(!drafts || drafts.length === 0) {
            container.innerHTML = "<p>No drafts.</p>";
            return;
        }
        
        container.innerHTML = drafts.map(draft => `
            <div class="item-card">
                <div class="item-header">
                    <span>To: ${draft.recipient}</span>
                    <span class="badge ${draft.state.toLowerCase()}">${draft.state} (v${draft.version})</span>
                </div>
                <div class="item-title">${draft.subject}</div>
                <div style="font-size: 0.8rem; margin-bottom: 8px; color: #f59e0b;">Source: ${draft.source}</div>
                <div class="item-body">${draft.body}</div>
                <div class="item-actions">
                    ${draft.state === 'draft' ? `
                        <button class="secondary-btn" onclick="openEditModal('${draft.id}', decodeURIComponent('${encodeURIComponent(draft.subject)}'), decodeURIComponent('${encodeURIComponent(draft.body)}'))">Edit</button>
                        <button class="success-btn" onclick="actDraft('${draft.id}', 'approve')">Approve</button>
                        <button class="danger-btn" onclick="actDraft('${draft.id}', 'reject')">Reject</button>
                    ` : ''}
                    ${draft.state === 'approved' ? `
                        <button class="primary-btn" onclick="actDraft('${draft.id}', 'send')">Send</button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }
    
    function renderTasks(tasks) {
        const container = document.getElementById('tasks-list');
        if(!tasks || tasks.length === 0) {
            container.innerHTML = "<p>No action items detected.</p>";
            return;
        }
        
        container.innerHTML = tasks.map(task => `
            <div class="item-card">
                <div class="item-header">
                    <span>Source: ${task.source_email}</span>
                    <span class="badge ${task.status === 'completed' ? 'completed' : 'pending'}">${task.status}</span>
                </div>
                <div class="item-title">${task.description}</div>
                <div class="item-body">
                    Assigned: ${task.assigned_to || 'Unassigned'} | Due: ${task.deadline || 'None'}
                    ${task.confidence !== undefined && task.confidence !== null ? `<br>Confidence: ${Math.round(task.confidence * 100)}%` : ''}
                </div>
                ${task.status === 'pending' ? `
                    <div class="item-actions">
                        <button class="success-btn" onclick="completeTask('${task.id}')">Complete</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    function renderMeetings(meetings) {
        const container = document.getElementById('meetings-list');
        if(!meetings || meetings.length === 0) {
            container.innerHTML = "<p>No meeting requests.</p>";
            return;
        }
        
        container.innerHTML = meetings.map(m => `
            <div class="item-card">
                <div class="item-header">
                    <span>${m.sender}</span>
                    <span class="badge ${m.status.toLowerCase()}">${m.status}</span>
                </div>
                <div class="item-title">${m.subject}</div>
                <div class="item-body">
                    Requested:<br>
                    ${m.proposed_date || 'Any'}${m.proposed_time ? ', ' + m.proposed_time : ''}${m.requested_slot_status === 'BUSY' ? ' — BUSY' : ''}
                </div>
                ${m.status === 'pending' && m.available_slots.length > 0 ? `
                    <div style="font-size:0.85rem; margin-top:8px; margin-bottom:4px; font-weight:bold;">
                        ${m.requested_slot_status === 'BUSY' ? 'Alternatives:' : 'Suggested slots:'}
                    </div>
                    <div class="item-actions">
                        <select id="slot-${m.id}" class="input-field" style="width:auto; padding:5px;">
                            ${m.available_slots.map(s => `<option value="${s}">${s}</option>`).join('')}
                        </select>
                        <button class="success-btn" onclick="confirmMeeting('${m.id}')">Confirm</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    function renderFollowUps(followups) {
        const container = document.getElementById('followups-list');
        if(!followups || followups.length === 0) {
            container.innerHTML = "<p>No follow-ups.</p>";
            return;
        }
        
        container.innerHTML = followups.map(f => `
            <div class="item-card">
                <div class="item-header">
                    <span>Due: ${new Date(f.reminder_at).toLocaleString()}</span>
                    <span class="badge ${f.status === 'completed' ? 'completed' : (f.is_due ? 'critical' : 'pending')}">${f.status}</span>
                </div>
                <div class="item-title">${f.email_subject}</div>
                ${f.status === 'pending' ? `
                    <div class="item-actions">
                        <button class="success-btn" onclick="completeFollowUp('${f.id}')">Complete</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    function renderAuditLog(log) {
        const container = document.getElementById('audit-list');
        if(!log || log.length === 0) {
            container.innerHTML = "<p>No history.</p>";
            return;
        }
        
        // Show newest first
        const reversedLog = [...log].reverse();
        
        container.innerHTML = reversedLog.map(entry => `
            <div class="item-card" style="padding: 10px;">
                <div style="font-size: 0.8rem; color: #94a3b8;">${new Date(entry.timestamp).toLocaleString()}</div>
                <div style="font-weight: 600;">${entry.actor} performed ${entry.action.toUpperCase()}</div>
                ${entry.recipient ? `<div style="font-size: 0.85rem; color: #cbd5e1;">Target: ${entry.recipient} - ${entry.subject}</div>` : ''}
            </div>
        `).join('');
    }
    
    // Global functions for inline onclick handlers
    window.openEditModal = (id, subject, body) => {
        document.getElementById('edit-draft-id').value = id;
        document.getElementById('edit-draft-subject').value = subject;
        document.getElementById('edit-draft-body').value = body;
        modal.style.display = 'flex';
    };
    
    window.actDraft = async (id, action) => {
        try {
            await fetch(`/api/drafts/${id}/${action}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reviewer: "Faculty User" })
            });
            await loadState();
        } catch(e) {
            alert(`Error performing ${action}: ` + e.message);
        }
    };
    
    window.completeTask = async (id) => {
        try {
            await fetch(`/api/tasks/${id}/complete`, { method: 'POST' });
            await loadState();
        } catch(e) {
            alert("Error completing task: " + e.message);
        }
    };
    
    window.completeFollowUp = async (id) => {
        try {
            await fetch(`/api/followups/${id}/complete`, { method: 'POST' });
            await loadState();
        } catch(e) {
            alert("Error completing follow-up: " + e.message);
        }
    };
    
    window.confirmMeeting = async (id) => {
        const slot = document.getElementById(`slot-${id}`).value;
        try {
            await fetch(`/api/meetings/${id}/confirm`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slot })
            });
            await loadState();
        } catch(e) {
            alert("Error confirming meeting: " + e.message);
        }
    };
    
    function escapeHtml(unsafe) {
        return (unsafe || "").replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initial load
    loadState();
});
