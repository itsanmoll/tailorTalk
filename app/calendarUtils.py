from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import pytz 
import re

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'assignments-464701-418734497e1c.json'
CALENDAR_ID = 'assignment@assignments-464701.iam.gserviceaccount.com'  # Replace with your real/test calendar ID

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

def check_availability(start_time: datetime, end_time: datetime):
    print("📅 Checking availability:")
    print(f"   Start: {start_time.isoformat()}")
    print(f"   End:   {end_time.isoformat()}")
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
     
    # """
    # Parses user input like 'Book a meeting tomorrow at 3 PM' and calls book_event.
    # """
    # try:
    #     summary = user_input
    #     start_time = datetime.now() + timedelta(days=1)
    #     start_time = start_time.replace(hour=15, minute=0, second=0)
    #     end_time = start_time + timedelta(minutes=30)

        
    #     busy_slots = check_availability(start_time, end_time)
    #     if busy_slots:
    #         return "❌ Time slot is already busy. Try another time."

    #     # Call actual booking function
    #     event_link = book_event(summary, start_time, end_time)
    #     return f"✅ Event booked successfully: {event_link}"

    # except Exception as e:
    #     return f"❌ Failed to book event: {str(e)}"
    print(f"🔧 [Tool Called] book_event_from_text() with input: {user_input}")
    try:
        now = datetime.now()
        summary = "Meeting"
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        user_lower = user_input.lower()
        day_offset = 1
        for idx, day in enumerate(weekdays):
            if day in user_lower:
                today_idx = now.weekday()
                delta = (idx - today_idx + 7) % 7
                day_offset = delta or 7 
                break
        event_date = now + timedelta(days=day_offset)

        try:
            parsed_dt = date_parser.parse(user_input, fuzzy=True, default=event_date)
            event_time= parsed_dt.time()
        except Exception as e:
            return "❌ Couldn't parse the meeting time."
            
        local_tz = pytz.timezone("Asia/Kolkata")
            
        event_date = now + timedelta(days=day_offset)
        # start_time = datetime.combine(event_date.date(), event_time)
        # start_time = start_time.replace(second=0, microsecond=0).astimezone(pytz.utc)
        start_time = local_tz.localize(datetime.combine(event_date.date(), event_time))
        start_time_utc = start_time.astimezone(pytz.utc)
            
        duration = timedelta(minutes=30)  # default
        duration_match = re.search(r'(\d+)\s*(minute|min|hour|hr)', user_lower)

        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2)
            if 'hour' in unit or 'hr' in unit:
                duration = timedelta(hours=value)
            else:
                duration = timedelta(minutes=value)
        end_time_utc = start_time_utc + duration

        busy = check_availability(start_time_utc, end_time_utc)

        if busy:
            return "⛔ That time is busy. Please try a different slot."
            
        link = book_event(summary, start_time_utc, end_time_utc)
        # local_start = start_time.astimezone(pytz.timezone("Asia/Kolkata")).strftime('%A %I:%M %p')
        # local_end = end_time.astimezone(pytz.timezone("Asia/Kolkata")).strftime('%I:%M %p')
        local_start = start_time.strftime('%A %I:%M %p')
        local_end = (start_time + duration).strftime('%I:%M %p')
        return f"✅ Meeting booked from {local_start} to {local_end}. [View event]({link})"

            
        # return f"✅ Meeting booked from {local_start} to {local_end}. [View event]({link})"
    except Exception as e :
        return f"❌ Failed to book event: {str(e)}"