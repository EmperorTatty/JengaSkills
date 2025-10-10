import json
import frappe
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build


@frappe.whitelist(allow_guest=True)
def create_google_meet_event(summary, start_time, end_time, attendees=None):
    try:
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)

        SCOPES = ['https://www.googleapis.com/auth/calendar']
        SERVICE_ACCOUNT_FILE = frappe.get_site_path('google_credentials.json')

        # 🔹 Use domain-wide delegation (replace with your domain user)
        DELEGATED_USER = "abedtati1@gmail.com"

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        delegated_creds = credentials.with_subject(DELEGATED_USER)

        service = build('calendar', 'v3', credentials=delegated_creds)

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

        return {
            "event_id": event.get('id'),
            "meet_link": event.get('hangoutLink')
        }

    except Exception as e:
        frappe.log_error(f"Google Meet creation failed: {str(e)}", "Google Meet API Error")
        return {"error": str(e)}
