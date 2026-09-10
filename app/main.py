""" from models import Email
from classifier import extract_action_items


test_emails = [
    Email(
        sender="student@gmail.com",
        subject="Project submission",
        body="Sir, please review my project report and submit the final marks by Friday."
    ),

    Email(
        sender="admin@university.edu",
        subject="Workshop information",
        body="The faculty development workshop will be conducted next Monday at 10 AM."
    ),

    Email(
        sender="student@gmail.com",
        subject="Assignment deadline",
        body="Sir, I will submit my assignment by tomorrow."
    ),

    Email(
        sender="researcher@iit.edu",
        subject="Research meeting",
        body="Can we meet next Wednesday at 2 PM to discuss our research paper?"
    )
]


for i, email in enumerate(test_emails, start=1):

    result = extract_action_items(email)

    print(f"\n--- Email {i} ---")
    print(f"Subject: {email.subject}")
    print(f"Action Items: {result.action_items}") 
    
from tools import read_inbox


emails = read_inbox()

for email in emails:
    print("\n--- Email ---")
    print("From:", email.sender)
    print("Subject:", email.subject)
    print("Body:", email.body)"""
    
from tools import lookup_contact


"""result = lookup_contact("researcher@iit.edu")

print("Contact information:")
print(result)
result = lookup_contact("unknown@gmail.com")
print(result)


from tools import check_deadline


days_remaining = check_deadline("2026-09-10")

print("Days remaining:", days_remaining)
print(check_deadline("Friday"))



from tools import read_inbox, get_email_context


emails = read_inbox()

for email in emails:
    context = get_email_context(email)

    print("\n========== EMAIL ==========")
    print("From:", email.sender)
    print("Subject:", email.subject)

    print("\nContact information:")
    print(context["contact"])
    

    
from tool_agent import find_email_context


result = find_email_context("researcher@iit.edu")

if result:
    print("\n========== EMAIL ==========")
    print("From:", result["email"].sender)
    print("Subject:", result["email"].subject)
    print("Body:", result["email"].body)

    print("\n========== CONTACT ==========")
    print(result["contact"])
else:
    print("Email not found.")
    
    
    
from skills import create_plan


email_plan = create_plan(
    goal="Organize faculty emails",
    scope="Unread emails from this week",
    priority_focus="Deadlines and urgent requests",
    output="Triaged inbox with draft replies"
)

print("EMAIL PLAN")
print(email_plan)


research_plan = create_plan(
    goal="Organize research papers",
    scope="Papers collected this month",
    priority_focus="Papers related to our current project",
    output="Prioritized research list"
)

print("\nRESEARCH PLAN")
print(research_plan)


from skills import create_plan, format_plan


email_plan = create_plan(
    goal="Organize faculty emails",
    scope="Unread emails from this week",
    priority_focus="Deadlines and urgent requests",
    output="Triaged inbox with draft replies"
)

print(format_plan(email_plan))


research_plan = create_plan(
    goal="Organize research papers",
    scope="Papers collected this month",
    priority_focus="Papers related to our current project",
    output="Prioritized research list"
)

print("\n" + format_plan(research_plan))



from memory import retrieve_by_tag


results = retrieve_by_tag("project")

print("Project-related memories:\n")

for memory in results:
    print("-", memory.content)
    print("  Tags:", memory.tags)
    
    
from memory import retrieve_by_similarity


query = "project deadline"

results = retrieve_by_similarity(query)

print("Similarity search results:\n")

for memory in results:
    print("-", memory.content)
    
    
from memory import store_memory, retrieve_by_tag


store_memory(
    "Student asked for an extension on the assignment.",
    ["student", "assignment", "extension"]
)

results = retrieve_by_tag("extension")

print("Extension-related memories:\n")

for memory in results:
    print("-", memory.content) 
    
    
from memory import SessionState


session = SessionState(
    run_id="run-001",
    user_request="Organize my unread emails"
)

session.current_plan = "Classify and prioritize unread emails"

session.current_email = "Project extension"

session.tool_results.append(
    "Inbox contains 3 emails"
)

print("========== SESSION STATE ==========")
print("Run ID:", session.run_id)
print("User request:", session.user_request)
print("Current plan:", session.current_plan)
print("Current email:", session.current_email)
print("Tool results:", session.tool_results)


from connector import EmailConnector


connector = EmailConnector()

emails = connector.get_inbox()

print("========== INBOX ==========")

for email in emails:
    print("From:", email.sender)
    print("Subject:", email.subject)

print("\n========== CONTACT ==========")

contact = connector.get_contact("researcher@iit.edu")

print(contact)

print("\n========== TASKS ==========")

tasks = connector.get_tasks()

print(tasks)


from connector import EmailConnector, MockEmailConnector


def test_connector(connector):
    print("\n========== INBOX ==========")

    emails = connector.get_inbox()

    for email in emails:
        print(email)

    print("\n========== CONTACT ==========")

    print(
        connector.get_contact("newstudent@gmail.com")
    )

    print("\n========== TASKS ==========")

    print(connector.get_tasks())


print("ORIGINAL CONNECTOR")
test_connector(EmailConnector())

print("\n\nMOCK CONNECTOR")
test_connector(MockEmailConnector())


from runtime import Runtime
from connector import EmailConnector


runtime = Runtime()
connector = EmailConnector()

emails = runtime.execute(
    "get_inbox",
    connector.get_inbox
)

print("Emails retrieved:", len(emails))

print("\n========== AUDIT LOG ==========")

for entry in runtime.audit_log:
    print("Action:", entry.action)
    print("Inputs:", entry.inputs)
    print("Outputs:", entry.outputs)
    print("Time:", entry.timestamp)
    
    
from runtime import Runtime
from connector import EmailConnector


runtime = Runtime()
connector = EmailConnector()


emails = runtime.execute(
    "get_inbox",
    connector.get_inbox
)

print("Emails retrieved:", len(emails))

print("\nCheckpoint:")
print(runtime.get_checkpoint())

print("\nResume information:")
print(runtime.resume())"""


from runtime import Runtime


runtime = Runtime()

approved = runtime.require_approval("send_reply")

if approved:
    print("\nAction approved by human.")
else:
    print("\nAction rejected by human.")


