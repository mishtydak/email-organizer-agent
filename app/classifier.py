from groq import Groq
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
import os
import json

load_dotenv()


# ============================================================
# DATA MODELS
# ============================================================

class ActionItem(BaseModel):
    description: str
    deadline: str | None
    assigned_to: str | None
    confidence: float


class ActionExtraction(BaseModel):
    action_items: list[ActionItem]


class EmailClassification(BaseModel):
    sender_category: Literal[
        "Student",
        "Admin",
        "Collaborator",
        "Vendor",
        "Other"
    ]

    email_type: Literal[
        "Request",
        "Information",
        "Meeting",
        "Complaint",
        "Deadline",
        "Notification",
        "Other"
    ]

    priority: Literal[
        "Critical",
        "High",
        "Medium",
        "Low"
    ]


class FallbackEmailClassification(EmailClassification):
    last_error: str | None = None


class FallbackActionExtraction(ActionExtraction):
    last_error: str | None = None


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# EMAIL CLASSIFICATION
# ============================================================

def classify_email(email):

    prompt = f"""
You are an email classification assistant for a university faculty member.

Classify the email based on:
1. Who sent it
2. What the email is about
3. Whether it requires faculty action
4. Deadlines
5. Urgency or escalation language

Return ONLY valid JSON in this exact format:

{{
    "sender_category": "Student",
    "email_type": "Request",
    "priority": "Medium"
}}

Allowed sender_category values:
- Student
- Admin
- Collaborator
- Vendor
- Other

Allowed email_type values:
- Request
- Information
- Meeting
- Complaint
- Deadline
- Notification
- Other

Allowed priority values:
- Critical
- High
- Medium
- Low

Email:

From: {email.sender}

Subject: {email.subject}

Body:
{email.body}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = response.choices[0].message.content

    data = json.loads(result)

    return EmailClassification.model_validate(data)


# ============================================================
# SAFE CLASSIFICATION
# ============================================================

def classify_email_safe(email):

    last_error = None

    try:
        return classify_email(email)

    except Exception as error:

        last_error = error

        print(f"Groq unavailable: {error}")
        print("Using fallback classification.")

        subject = email.subject.lower()
        body = email.body.lower()

        # ----------------------------------------------------
        # Sender category
        # ----------------------------------------------------

        if "student" in body or "student" in subject:
            sender_category = "Student"

        elif "admin" in body or "administration" in body:
            sender_category = "Admin"

        elif "unstop" in email.sender.lower():
            sender_category = "Vendor"

        else:
            sender_category = "Other"

        # ----------------------------------------------------
        # Email type
        # ----------------------------------------------------

        if "meeting" in subject or "meeting" in body:
            email_type = "Meeting"

        elif "deadline" in subject or "deadline" in body:
            email_type = "Deadline"

        elif "request" in subject or "please" in body:
            email_type = "Request"

        elif "complaint" in subject or "complaint" in body:
            email_type = "Complaint"

        else:
            email_type = "Information"

        # ----------------------------------------------------
        # Priority
        # ----------------------------------------------------

        if any(
            word in subject + " " + body
            for word in ["urgent", "immediately", "critical"]
        ):
            priority = "Critical"

        elif any(
            word in subject + " " + body
            for word in ["asap", "important", "today"]
        ):
            priority = "High"

        else:
            priority = "Medium"

        result = FallbackEmailClassification(
            sender_category=sender_category,
            email_type=email_type,
            priority=priority
        )

        result.last_error = str(last_error)

        return result


# ============================================================
# ACTION ITEM EXTRACTION
# ============================================================

def extract_action_items(email):

    prompt = f"""
You are an action-item extraction assistant for a university faculty member.

Read the email and identify tasks that someone is explicitly expected to perform.

Rules:
- Extract only real, actionable tasks.
- Do not invent tasks.
- If there are no action items, return an empty list.
- Extract the deadline if one is mentioned.
- Identify who is expected to perform the task if it is clear.
- If the deadline or assignee is not mentioned, use null.
- Confidence must be a number between 0 and 1.

Return ONLY valid JSON in this exact format:

{{
    "action_items": [
        {{
            "description": "Review the research paper",
            "deadline": "Friday",
            "assigned_to": "Faculty",
            "confidence": 0.95
        }}
    ]
}}

If there are no action items, return:

{{
    "action_items": []
}}

Email:

From: {email.sender}

Subject: {email.subject}

Body:
{email.body}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = response.choices[0].message.content

    data = json.loads(result)

    return ActionExtraction.model_validate(data)


# ============================================================
# SAFE ACTION EXTRACTION
# ============================================================

def extract_action_items_safe(email):

    last_error = None

    try:
        return extract_action_items(email)

    except Exception as error:

        last_error = error

        print(f"Groq action extraction unavailable: {error}")
        print("Using empty action-item fallback.")

        result = FallbackActionExtraction(
            action_items=[]
        )

        result.last_error = str(last_error)

        return result