
import os
from google.auth.transport.requests import Request
import frappe
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and return Google Calendar API service."""
    creds = None

    creds_file = frappe.get_site_path('google_credentials.json')
    token_file = frappe.get_site_path('token.json')

    # Load existing token or start new flow
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


@frappe.whitelist()
# @frappe.whitelist()
def create_google_meet_event(summary, start_time, end_time, attendees=None):
    """Create a Google Meet event in the authorized user's calendar."""
    try:
        service = get_calendar_service()

        event = {
            'summary': summary,
            'description': 'Automatically generated class session via ERPNext',
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Africa/Nairobi'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Africa/Nairobi'},
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
        }

        # Include attendees if provided
        if attendees:
            event['attendees'] = attendees

        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        meet_link = event.get('hangoutLink') or event['conferenceData']['entryPoints'][0]['uri']
        return {'event_id': event['id'], 'meet_link': meet_link}

    except Exception as e:
        frappe.log_error(f"Google Meet Error: {str(e)}", "Google Meet Integration")
        return {"error": str(e)}

