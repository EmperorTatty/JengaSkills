from urllib.request import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Define the OAuth scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Path to your credentials JSON file
creds_file = "/home/abeddy/JengaSkills/sites/skills.com/google_credentials.json"


def main():
    creds = None
    token_file = "token.json"

    # Load or request new credentials
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            # creds = flow.run_local_server(port=0)
            creds = flow.run_local_server(port=8080)

        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    # Build the Calendar API service
    service = build('calendar', 'v3', credentials=creds)

    # Create a test event
    event = {
        'summary': 'ERPNext Google Meet Test',
        'start': {'dateTime': '2025-11-07T15:00:00+03:00'},
        'end': {'dateTime': '2025-11-07T15:30:00+03:00'},
        'conferenceData': {
            'createRequest': {
                'requestId': 'test123',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        },
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    print("✅ Event created:")
    print("📅", event.get('summary'))
    print("🔗 Meet Link:", event['conferenceData']['entryPoints'][0]['uri'])

if __name__ == '__main__':
    main()
