import json
import frappe
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

def create_google_meet_event(summary, start_time, end_time, attendees=None):
    """
    Creates a Google Calendar event with Meet link.
    Returns event ID and meet link.
    """
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        SERVICE_ACCOUNT_FILE = frappe.get_site_path('google_credentials.json')

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        service = build('calendar', 'v3', credentials=credentials)

        event = {
            'summary': summary,
            'description': 'Automatically generated class session via ERPNext',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Africa/Nairobi',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Africa/Nairobi',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"{summary}-{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
            'attendees': attendees or []
        }

        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        return event['id'], event['hangoutLink']

    except Exception as e:
        frappe.log_error(f"Google Meet creation failed: {str(e)}", "Google Meet API Error")
        return None, None
