import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Tailored of off Google API's quickstart guide: https://developers.google.com/calendar/api/quickstart/python
class GoogleCalendar:

    # If modifying these scopes, delete the file token.json.
    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ]
    existing_events = []

    def __init__(self):
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=65490)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        self.creds = creds
        self.service = build("calendar", "v3", credentials=creds)

    def get_events(self, timeMin=None, timeMax=None, maxResults=5):
        now = timeMin or datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                timeMax=timeMax,
                maxResults=maxResults,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    def create_event(self, new_event):
        event = (
            self.service.events().insert(calendarId="primary", body=new_event).execute()
        )
        return event.get("htmlLink")

    def already_exists(self, new_event):
        events = self.get_events(
            new_event["start"]["dateTime"], new_event["end"]["dateTime"]
        )
        for event in events:
            if (
                event["summary"] == new_event["summary"]
                and event["start"]["dateTime"] == new_event["start"]["dateTime"]
            ):
                return True

        return False
