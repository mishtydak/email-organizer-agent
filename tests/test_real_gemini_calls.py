import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from classifier import classify_email, classify_email_safe, extract_action_items, extract_action_items_safe

class MockEmail:
    def __init__(self, sender, subject, body):
        self.sender = sender
        self.subject = subject
        self.body = body

email = MockEmail("student@university.edu", "Late Assignment Request", "Hi, I need an extension for my homework because I was sick.")

print("--- Testing classify_email (Real Gemini) ---")
try:
    res = classify_email(email)
    print("Success! Response:", res)
    print("sender_category:", res.sender_category)
except Exception as e:
    print("Failed:", type(e), e)

print("\n--- Testing classify_email_safe ---")
try:
    res2 = classify_email_safe(email)
    print("Safe Response:", res2)
    print("Source:", getattr(res2, 'source', 'unknown'))
except Exception as e:
    print("Safe Failed:", type(e), e)

print("\n--- Testing extract_action_items (Real Gemini) ---")
try:
    res3 = extract_action_items(email)
    print("Success! Response:", res3)
except Exception as e:
    print("Failed:", type(e), e)

print("\n--- Testing extract_action_items_safe ---")
try:
    res4 = extract_action_items_safe(email)
    print("Safe Response:", res4)
    print("Source:", getattr(res4, 'source', 'unknown'))
except Exception as e:
    print("Safe Failed:", type(e), e)
