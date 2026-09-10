import sys
import os
sys.path.append('app')
from dotenv import load_dotenv
load_dotenv()

from classifier import classify_email_safe, extract_action_items_safe

class MockEmail:
    def __init__(self, subject, body, sender="student@example.com"):
        self.subject = subject
        self.body = body
        self.sender = sender

email = MockEmail(
    subject="Research Paper Review \u2013 Follow-up Required",
    body="Dear Professor,\n\nI have shared the updated research paper for your review.\n\nCould you please review it and get back to me in 2 days with your feedback?\nI would like to make the necessary changes based on your suggestions.\n\nThank you.\nRegards,\nStudent"
)

cls = classify_email_safe(email)
print("Classification:", cls)

ext = extract_action_items_safe(email)
print("Action Extraction:", ext)
