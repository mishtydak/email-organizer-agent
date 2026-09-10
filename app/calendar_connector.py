import os
from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.freebusy"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "credentials.json"
)

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "calendar_token.json"
)


def get_calendar_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build(
        "calendar",
        "v3",
        credentials=creds
    )


class GoogleCalendarConnector:

    def __init__(self):
        self.service = get_calendar_service()

    def get_busy_periods(
        self,
        time_min: datetime,
        time_max: datetime,
        calendar_id: str = "primary"
    ):
        response = (
            self.service
            .freebusy()
            .query(
                body={
                    "timeMin": time_min.astimezone(
                        timezone.utc
                    ).isoformat(),
                    "timeMax": time_max.astimezone(
                        timezone.utc
                    ).isoformat(),
                    "timeZone": "UTC",
                    "items": [
                        {
                            "id": calendar_id
                        }
                    ]
                }
            )
            .execute()
        )

        calendar_data = response[
            "calendars"
        ][calendar_id]

        return calendar_data.get(
            "busy",
            []
        )