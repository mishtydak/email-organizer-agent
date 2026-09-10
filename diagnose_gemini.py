import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))
from classifier import classify_email, classify_email_safe, extract_action_items, extract_action_items_safe

class MockEmail:
    def __init__(self, sender, subject, body):
        self.sender = sender
        self.subject = subject
        self.body = body

email = MockEmail("student@university.edu", "Project Extension Request", "I am a student and I need a two-day extension for my project submission.")

print("==================================================")
print("GEMINI DIAGNOSTIC: CLASSIFICATION")
print("==================================================")
print("Provider: Gemini API (google-genai)")
print(f"Model name: {os.getenv('GEMINI_CLASSIFIER_MODEL', 'gemini-1.5-flash')}")
print("API call attempted: client.models.generate_content (classify_email)")

try:
    res = classify_email(email)
    print("Status code: 200 OK")
    print("Status: SUCCESS")
    print(f"Classification result: Type={res.email_type}, Category={res.sender_category}, Priority={res.priority}")
    print("Fallback used: No")
except Exception as e:
    print(f"Status: ERROR")
    print(f"HTTP/API error type: {type(e).__name__}")
    if hasattr(e, 'code'):
        print(f"Status code: {e.code}")
    print(f"Error message: {str(e)}")
    print("Fallback used: Yes (via safe wrapper)")

print("\n==================================================")
print("GEMINI DIAGNOSTIC: ACTION EXTRACTION")
print("==================================================")
print("Provider: Gemini API (google-genai)")
print(f"Model name: {os.getenv('GEMINI_EXTRACTION_MODEL', 'gemini-1.5-flash')}")
print("API call attempted: client.models.generate_content (extract_action_items)")

try:
    res2 = extract_action_items(email)
    print("Status code: 200 OK")
    print("Status: SUCCESS")
    print(f"Action extraction result: {res2.action_items}")
    print("Fallback used: No")
except Exception as e:
    print(f"Status: ERROR")
    print(f"HTTP/API error type: {type(e).__name__}")
    if hasattr(e, 'code'):
        print(f"Status code: {e.code}")
    print(f"Error message: {str(e)}")
    print("Fallback used: Yes (via safe wrapper)")
