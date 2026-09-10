import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from models import Email


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

def get_gmail_service():
    creds = None

    # Reuse previously saved login
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Login if credentials are missing or invalid
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save login token for future runs
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


class GmailConnector:

    def __init__(self):
        self.service = get_gmail_service()

    def list_message_ids(self, max_results=5):

        response = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                maxResults=max_results
            )
            .execute()
        )

        return response.get("messages", [])
    
    def get_email(self, message_id):

     response = (
        self.service
        .users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full"
        )
        .execute()
     )

     headers = response[
        "payload"
     ].get(
        "headers",
        []
     )

     sender = ""
     subject = ""

     for header in headers:

        name = header["name"].lower()

        if name == "from":
            sender = header["value"]

        elif name == "subject":
            subject = header["value"]

     body = response.get(
        "snippet",
        ""
     )

     return Email(
        sender=sender,
        subject=subject,
        body=body,
        message_id=response.get("id"),
        thread_id=response.get("threadId")
     )

   
    def fetch_emails(self, max_results=5):
      messages = self.list_message_ids(max_results)

      emails = []

      for message in messages:
        email = self.get_email(message["id"])
        emails.append(email)

      return emails
    
    def get_thread(self, thread_id):
     response = (
        self.service
        .users()
        .threads()
        .get(
            userId="me",
            id=thread_id,
            format="full"
        )
        .execute()
    )

     return response


    def get_thread_messages(self, thread_id):
     thread = self.get_thread(thread_id)

     return thread.get("messages", [])

  