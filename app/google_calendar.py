import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class GoogleCalendar:

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        self.creds = creds
        self.service = build('calendar', 'v3', credentials=creds)

    def get_events(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
        return events_result.get('items', [])

    def create_event(self, new_event):
        if not self.already_exists(new_event):
            event = self.service.events().insert(calendarId='primary', body=new_event).execute()
            return event.get('htmlLink')
        else:
            return 'Event Already Exists'

    def already_exists(self, new_event):
        events = self.get_date_events(new_event['start']['dateTime'], self.get_events())
        event_list = [new_event['summary'] for new_event in events]
        if new_event['summary'] not in event_list:
            return False
        else:
            return True

    def get_date_events(self, date, events):
        lst = []
        date = date
        for event in events:
            if event.get('start').get('dateTime'):
                d1 = event['start']['dateTime']
                if d1 == date:
                    lst.append(event)
        return lst