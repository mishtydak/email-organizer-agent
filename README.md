# Email Organizer Agent

An agentic AI email triage assistant designed to organize incoming emails, determine priorities, extract action items, identify meeting requests, generate context-grounded draft replies, and manage follow-ups. 

The volume of daily academic and professional emails can easily overwhelm standard inboxes. Traditional chatbots are purely reactive, requiring constant manual prompting. This project utilizes an **agentic architecture** that proactively polls the inbox, builds structured internal representations of emails, conducts deep research on previous threads, parallelizes sub-agent processing, and routes everything into a unified review queue. 

**Core Safety Principle:** This system operates strictly as a decision-support and triage assistant, **not** a fully autonomous inbox agent. It employs a strict **human-in-the-loop (HITL)** design. The system will NEVER automatically send emails, silently confirm calendar meetings, or mark action items as complete without explicit human approval.

## Features

The following features are fully implemented and integrated:
*   **Gmail Ingestion:** Secure OAuth connection to fetch live emails.
*   **AI Classification:** Categorizes sender (Student/Admin/etc.), email type (Request/Deadline/etc.), and priority (Critical/High/Medium/Low) using Groq.
*   **Action-Item Extraction:** Identifies discrete tasks with associated deadlines and assignees.
*   **Meeting-Request Detection:** Identifies meeting requests and uses the Google Calendar API to check free/busy schedules and suggest available slots.
*   **Thread Grounding:** Fetches actual prior messages in a Gmail thread to ground generated draft responses in factual history.
*   **Draft Reply Generation:** Generates contextual reply drafts using the `openai/gpt-oss-20b` model.
*   **Draft Review Queue:** A staging area (`DRAFT` → `APPROVED` / `REJECTED`) blocking unauthorized sends.
*   **Gmail Sending:** Outgoing emails are sent via the Gmail API **only** after explicit human approval.
*   **Follow-Up & Task Management:** Tracks pending tasks. Scheduling a follow-up triggers a synchronized state (completing a task automatically marks the related follow-up as handled).
*   **Audit Logging:** Tracks every manual and automated state change, recording the actor and timestamp.
*   **Retry / Self-Healing:** Graceful fallback behaviors if the primary AI API (Groq) or external connectors fail.
*   **Dashboard:** A custom Flask-based web UI for reviewing the triaged inbox, managing drafts, confirming meetings, and viewing pipeline diagnostics.

## Agent Architecture

The system utilizes a modular, graph-based architecture where specialized sub-agents handle discrete responsibilities.

*   **Coordinator:** Determines the overall processing plan for incoming batches.
*   **Ingestion / Classification:** Safely fetches and labels incoming emails.
*   **Draft Reply Agent:** Generates responses based on standard templates and thread history.
*   **Action Item / Follow-up Agent:** Parses deadlines and schedules reminders.
*   **Calendar Agent:** Interfaces with the Calendar API to negotiate meeting slots.
*   **Archive / Logging:** Maintains the history and audit trails.

```text
Incoming Email
      ↓
Gmail Ingestion
      ↓
Classification (Sender, Type, Priority)
      ↓
 ┌───────────────┬───────────────┬───────────────┐
 ↓               ↓               ↓
Priority       Actions        Meeting
 ↓               ↓               ↓
Draft Reply    Tasks       Calendar Check
 └───────────────┴───────────────┘
                  ↓
       Thread Grounding / Validation
                  ↓
             Faculty Review
                  ↓
          Approve / Reject / Edit
                  ↓
             Send if Approved
                  ↓
             Audit Logging
```

## Agentic Workflow

1. **Ingest email:** The Gmail connector fetches new, unread messages.
2. **Classify email:** Groq evaluates the email to determine the sender category and email type.
3. **Determine priority:** Flags emails as Critical, High, Medium, or Low.
4. **Extract action items:** Identifies requested tasks and deadlines.
5. **Detect meeting requests:** If a meeting is requested, it checks Calendar availability.
6. **Ground information:** Queries the Gmail API for previous messages in the thread to provide context.
7. **Generate a draft response:** Uses the grounded context to draft an intelligent reply.
8. **Validate output:** Checks the draft against formatting and safety constraints.
9. **Place draft into review queue:** The draft is stored in memory with a `DRAFT` state.
10. **Faculty/user reviews:** The user opens the Dashboard to view the processed inbox.
11. **Approve, edit, or reject:** The user edits the draft if necessary and marks it `APPROVED`.
12. **Send only after approval:** The system calls the Gmail Send API.
13. **Track actions/follow-ups:** The user manually confirms tasks/meetings as they are completed.
14. **Log important operations:** The system records the approval and sending actions to the Audit Log.

## Technology Stack

*   **Python 3**
*   **Groq API:** Fast LLM inference (`openai/gpt-oss-20b`).
*   **Gmail API:** OAuth2 authentication, reading threads, and sending emails.
*   **Google Calendar API:** Free/busy schedule extraction.
*   **Flask / Vanilla JS:** Powers the frontend dashboard and backend REST API (Streamlit is NOT used).
*   **Pydantic:** Strict schema validation for AI outputs.
*   **python-dotenv:** Secure environment variable management.
*   **concurrent.futures (ThreadPoolExecutor):** Enables parallel swarm processing for multiple emails.

## Project Structure

```text
email-organizer/
├── app/
│   ├── dashboard.py           # Flask application entry point
│   ├── dashboard_service.py   # Core workflow engine integrating all agents
│   ├── classifier.py          # Groq-powered classification and extraction
│   ├── gmail_connector.py     # Gmail API integration
│   ├── calendar_connector.py  # Calendar API integration
│   ├── graph.py               # Node graph state machine logic
│   ├── swarm.py               # Parallel processing executor
│   ├── task_manager.py        # Follow-up and task state management
│   ├── review_queue.py        # Draft governance and approval states
│   ├── audit.py               # Audit logging system
│   ├── tests/                 # Unit and integration test suite
│   ├── static/                # CSS and Vanilla JS for the dashboard
│   └── templates/             # HTML templates for Flask
├── tests/                     # Additional acceptance tests
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore file (excludes secrets)
└── README.md                  # This document
```

## Installation

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/mishtydak/email-organizer-agent.git
   cd email-organizer-agent
   ```
2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```
3. **Activate it:**
   ```powershell
   .\venv\Scripts\activate
   ```
4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
5. **Configure environment variables:**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
6. **Configure Google APIs:**
   * Place your `credentials.json` file in the `app/` directory (see Gmail/Calendar setup below).
7. **Run the dashboard:**
   ```powershell
   python app/dashboard.py
   ```
   Navigate to `http://127.0.0.1:5000` in your browser.

## Environment Variables

This project requires a `.env` file at the root of the directory to store secrets securely. 
*   `GROQ_API_KEY`: Your API key for Groq inference.

**CRITICAL:** Never commit `.env`, `credentials.json`, `token.json`, or `calendar_token.json` to version control. They are explicitly ignored in `.gitignore`.

## Gmail Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Gmail API**.
3. Configure the OAuth Consent Screen (add your email as a test user).
4. Create OAuth 2.0 Client IDs (Desktop Application).
5. Download the JSON file, rename it to `credentials.json`, and place it in the `app/` directory.
6. The application requests `gmail.readonly` and `gmail.send` scopes. Upon first run, a browser window will open to authorize access and generate `token.json`.

## Google Calendar Setup

1. In the same Google Cloud project, enable the **Google Calendar API**.
2. The application uses the same `credentials.json` to authenticate.
3. It requests `calendar.readonly` scopes to query free/busy intervals and generate non-conflicting meeting proposals.

## Usage

Start the Flask server via `python app/dashboard.py` and open the web UI.

**Typical Flow Example:**
*   **Incoming email:** "Could you please review my project report by Friday?"
*   Click **"Process Inbox"** on the dashboard.
*   **Backend processing:**
    *   Classification: Evaluated as `Student` / `Request` / `Medium` priority.
    *   Action Item: Extracts "Review project report" with deadline "Friday".
    *   Draft: Generates a polite acknowledgment draft.
*   **Dashboard Interaction:**
    *   The email appears in the **Triaged Inbox**.
    *   The task appears in **Action Items**.
    *   The draft waits in the **Draft Queue**.
    *   The user clicks **Edit**, modifies the draft, and clicks **Approve**.
    *   The user clicks **Send** to dispatch the email.
    *   Later, the user clicks **Complete** on the action item, automatically resolving the linked follow-up.

## Dashboard

The custom Flask dashboard provides full visibility into the agent's state:

*   **Triaged Inbox:** Displays ingested emails with AI-assigned priority and sender tags. Shows thread-grounding evidence.
*   **Draft Queue:** Allows editing, approving, rejecting, and sending AI-generated drafts.
*   **Action Items:** A checklist of extracted tasks and deadlines.
*   **Meeting Requests:** Highlights emails requesting meetings alongside available Calendar slots for confirmation.
*   **Follow-ups:** Reminders for high-priority items or pending tasks.
*   **Approval History (Audit Log):** An immutable list of who performed what action and when.
*   **System Diagnostics:** Real-time connection status for Gmail, Calendar, and the Groq API.
*   **Agent Pipeline:** Visualizes the success/fallback state of the multi-stage DAG graph.
*   **KPI Cards:** Quick metrics on pending approvals and review times.

## Safety and Governance

### No Auto-Send
Emails are **never** sent automatically. The system will raise a `PermissionError` if an attempt is made to send a draft that is not explicitly in the `APPROVED` state.

### Human Approval
The faculty/user maintains absolute final authority. The system operates as a draft-generator; the human is the dispatcher.

### Task Confirmation
Tasks and follow-ups remain pending until explicitly confirmed by the user via the UI. Completing a task syncs the state and completes the associated follow-up, preventing duplicate efforts.

### Meeting Confirmation
While the system parses Calendar availability and suggests slots, it will not auto-reply or auto-book meetings without human selection and approval.

### Auditability
All major state transitions (e.g., `approve_email`, `reject_email`, `complete_task`) are permanently recorded in the audit log with timestamps and actor tracking.

### Scope
The connector specifically scopes email reading and restricts operations to a controlled boundary, ensuring it cannot perform destructive inbox operations (like bulk deletion).

### Grounding
To prevent AI hallucination, the draft agent fetches previous messages from the specific email thread (`threadId`) using the Gmail API. Output that cannot be grounded in this retrieved history is flagged or rejected.

## Agentic AI Concepts Demonstrated

| Lab | Concept | How this project demonstrates it |
|-----|---------|----------------------------------|
| Lab 1 | Agent vs Chatbot | Moves beyond simple Q&A by proactively proposing, refining, and executing a multi-step triage plan. |
| Lab 2 | Tool-Using Agent | Agents utilize strict interfaces (`GmailConnector`, `check_deadline`) to interact with the outside world. |
| Lab 3 | Skill Creation | Employs reusable formatting and reasoning skills applied across different email contexts. |
| Lab 4 | Memory & Retrieval | Maintains session state (draft queues) while grounding responses in long-term retrieved thread history. |
| Lab 5 | MCP-style Connector | Abstracts Gmail and Calendar APIs into modular connectors, allowing backend swaps without agent logic changes. |
| Lab 6 | Runtime | Manages the execution context, enforces approval gates, and logs state transitions. |
| Lab 7 | Agentic Node Graph | The pipeline is modeled as a DAG (`ingest` → `classify` → `draft` → `validate`), with back-edges for self-correction. |
| Lab 8 | Parallel Swarm | Utilizes `ThreadPoolExecutor` to process multiple incoming emails concurrently, dramatically reducing wall-clock time. |
| Lab 9 | Deep Research / Grounding | Interrogates the Gmail API for historical thread context to ensure drafts are factually anchored. |
| Lab 10 | Operational Resilience | Employs `_safe` wrapper functions and bounded retries to gracefully fallback if the Groq API experiences downtime. |
| Lab 11 | SDLC / Acceptance | Governed by explicit agent specifications and backed by automated test suites simulating the pipeline. |
| Lab 12 | Safety / Governance | Implements strict human-in-the-loop review queues, preventing autonomous sending and tracking audit histories. |
| Lab 13 | Discipline-Specific Agents | Splits complex reasoning into specialist sub-agents (e.g., `meeting_agent.py` parsing strict datetime schemas). |
| Lab 14 | Capstone Integration | Culminates in a unified Flask dashboard that brings the connectors, parallel swarm, governance, and specialist agents into a single product. |

## Testing

The repository contains an extensive testing suite in the `tests/` directory and root level, focusing on integration and behavior:
*   **Classification & Extraction:** Verifies Groq's ability to output strict JSON schemas for priorities and action items.
*   **Gmail Ingestion & Grounding:** Tests verifying that `threadId` extraction successfully retrieves prior messages.
*   **Calendar Availability:** Tests mocking busy intervals to ensure alternative slots are accurately proposed.
*   **Governance & Review Queue:** Asserts that unapproved drafts throw errors if a send is attempted.
*   **Synchronization:** Tests (`test_sync.py`) confirming that completing a task clears the corresponding follow-up.
*   **Retry / Recovery:** Tests confirming graceful heuristic fallbacks when API access is denied.

## Security

*   Never commit `.env` containing your `GROQ_API_KEY`.
*   Never commit `credentials.json`, `token.json`, or `calendar_token.json`.
*   A strict `.gitignore` is included to prevent accidental exposure of these files.
*   If you accidentally expose a key or token, revoke it immediately via the Google Cloud Console or Groq Dashboard.

## Limitations
*   **Pagination:** Currently, the system ingests a fixed batch of emails at a time (e.g., `max_results=5`) rather than fully paginating through massive unread inboxes.
*   **Token Expiry:** If the Google OAuth refresh token fully expires, the backend will fail quietly; the user must manually delete `token.json` and re-authenticate.
*   **Complex Attachments:** The system currently processes plain text and snippets. It does not parse complex PDF or image attachments for action items.

## Future Improvements
*   Implement explicit rate-limit backoffs (e.g., HTTP 429 handling) for burst LLM API requests.
*   Add dynamic pagination to process historical inbox backlogs.
*   Introduce micro-animations in the UI to better reflect asynchronous background tasks.
*   Extend the Calendar Agent to directly write confirmed meetings to the Google Calendar (currently read-only for availability).

## Demo Flow
To present this project in an academic or professional setting:
1. **Start Dashboard:** Run `python app/dashboard.py` and open the browser.
2. **Ingest Gmail:** Click "Process Inbox" to fetch live emails.
3. **Show Classification:** Point out how emails are tagged (e.g., "Student", "High Priority").
4. **Show Extracted Action Item:** Navigate to the Action Items panel to show the parsed deadline.
5. **Show Meeting Request:** Demonstrate how an email requesting a meeting automatically pulls 3 available slots from Google Calendar.
6. **Show Generated Draft:** Open a drafted response and point out how it references previous thread history (Grounding).
7. **Show Review Queue:** Edit the draft slightly, click "Approve".
8. **Demonstrate Safety:** Explain that until approved, the "Send" button is unavailable.
9. **Show Audit History:** Navigate to the Audit Log to show that your approval was recorded.
10. **Show Synchronization:** Click "Complete" on an Action Item and show how the corresponding Follow-up automatically disappears.

## Conclusion
The Email Organizer Agent demonstrates a pragmatic implementation of Agentic AI. Rather than attempting fully autonomous and risky operations, it acts as a force multiplier for human decision-making. By combining parallelized AI reasoning with strict governance, API integrations, and a deterministic review queue, it solves the problem of inbox overload safely and efficiently.
