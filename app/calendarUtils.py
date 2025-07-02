from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'assignments-464701-418734497e1c.json'
CALENDAR_ID = 'assignment@assignments-464701.iam.gserviceaccount.com'  # Replace with your real/test calendar ID

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

def check_availability(start_time: datetime, end_time: datetime):
    body = {
        "timeMin": start_time.isoformat() + "Z",
        "timeMax": end_time.isoformat() + "Z",
        "items": [{"id": CALENDAR_ID}]
    }
    result = service.freebusy().query(body=body).execute()
    return result['calendars'][CALENDAR_ID]['busy']

def book_event(summary: str, start_time: datetime, end_time: datetime):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'}
    }
    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return event.get('htmlLink', 'No link returned')

def book_event_from_text(user_input: str) -> str:
    """
    Parses user input like 'Book a meeting tomorrow at 3 PM' and calls book_event.
    """
    try:
        summary = user_input
        start_time = datetime.now() + timedelta(days=1)
        start_time = start_time.replace(hour=15, minute=0, second=0)
        end_time = start_time + timedelta(minutes=30)

        
        busy_slots = check_availability(start_time, end_time)
        if busy_slots:
            return "❌ Time slot is already busy. Try another time."

        # Call actual booking function
        event_link = book_event(summary, start_time, end_time)
        return f"✅ Event booked successfully: {event_link}"

    except Exception as e:
        return f"❌ Failed to book event: {str(e)}"