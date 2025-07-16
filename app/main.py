# FastAPI backend for meeting booking bot
from typing import List, Tuple, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, validator
import re
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TailorTalk API",
    description="AI-powered calendar booking assistant",
    version="1.0.0"
)

class MeetingDetails(BaseModel):
    date: str
    time: str
    participants: List[EmailStr]
    agenda: Optional[str] = None
    duration: Optional[int] = 30  # Default 30 minutes
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Time must be in HH:MM format (24-hour)')

class ChatInput(BaseModel):
    user_input: str
    chat_history: List[Tuple[str, str]] = []

class MeetingResponse(BaseModel):
    message: str
    details: Optional[MeetingDetails] = None
    success: bool = True
    error_code: Optional[str] = None

def extract_meeting_details(user_input: str) -> Optional[MeetingDetails]:
    """Enhanced meeting details extraction with better parsing"""
    try:
        # Date patterns: YYYY-MM-DD, tomorrow, next week, etc.
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
            r'\b(tomorrow)\b',
            r'\b(next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b',
            r'\b(in\s+\d+\s+days?)\b'
        ]
        
        # Time patterns: HH:MM, 3 PM, 15:30, etc.
        time_patterns = [
            r'\b(\d{1,2}:\d{2})\b',  # HH:MM
            r'\b(\d{1,2}\s*(am|pm))\b',  # 3 PM, 3pm
            r'\b(\d{1,2}:\d{2}\s*(am|pm))\b'  # 3:30 PM
        ]
        
        # Duration patterns
        duration_patterns = [
            r'\b(\d+)\s*(minute|min|hour|hr)s?\b',
            r'\bfor\s+(\d+)\s*(minute|min|hour|hr)s?\b'
        ]
        
        # Extract date
        date_match = None
        for pattern in date_patterns:
            date_match = re.search(pattern, user_input.lower())
            if date_match:
                break
        
        # Extract time
        time_match = None
        for pattern in time_patterns:
            time_match = re.search(pattern, user_input.lower())
            if time_match:
                break
        
        # Extract participants (email addresses)
        participants_match = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', user_input)
        
        # Extract agenda
        agenda_patterns = [
            r'agenda[:\-]?\s*(.*?)(?=\s+(?:with|for|on|at)|$)',
            r'about\s+(.*?)(?=\s+(?:with|for|on|at)|$)',
            r'titled\s+[\'"](.*?)[\'"]',
            r'meeting\s+(?:about|regarding)\s+(.*?)(?=\s+(?:with|for|on|at)|$)'
        ]
        
        agenda_match = None
        for pattern in agenda_patterns:
            agenda_match = re.search(pattern, user_input, re.IGNORECASE)
            if agenda_match:
                break
        
        # Extract duration
        duration_match = None
        for pattern in duration_patterns:
            duration_match = re.search(pattern, user_input.lower())
            if duration_match:
                break
        
        # Process extracted data
        if date_match and time_match and participants_match:
            # Convert relative dates to absolute dates
            date_str = date_match.group(1)
            if date_str == 'tomorrow':
                date_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            elif date_str.startswith('next '):
                # Handle "next monday" etc.
                day_name = date_str.split()[1]
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                target_day = days.index(day_name)
                current_day = datetime.now().weekday()
                days_ahead = (target_day - current_day + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7
                date_str = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            # Process time
            time_str = time_match.group(1)
            if 'pm' in time_str.lower() and not time_str.startswith('12'):
                # Convert 12-hour to 24-hour format
                time_parts = re.findall(r'(\d{1,2}):?(\d{2})?', time_str)
                if time_parts:
                    hour = int(time_parts[0][0])
                    minute = int(time_parts[0][1]) if time_parts[0][1] else 0
                    hour = hour + 12 if hour < 12 else hour
                    time_str = f"{hour:02d}:{minute:02d}"
            
            # Process duration
            duration = 30  # default
            if duration_match:
                value = int(duration_match.group(1))
                unit = duration_match.group(2)
                if 'hour' in unit or 'hr' in unit:
                    duration = value * 60
                else:
                    duration = value
            
            return MeetingDetails(
                date=date_str,
                time=time_str,
                participants=participants_match,
                agenda=agenda_match.group(1).strip() if agenda_match else None,
                duration=duration
            )
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting meeting details: {e}")
        return None

@app.post("/book_meeting", response_model=MeetingResponse)
async def book_meeting_endpoint(payload: ChatInput):
    """Enhanced meeting booking endpoint with better validation"""
    try:
        details = extract_meeting_details(payload.user_input)
        if not details:
            return MeetingResponse(
                message="❌ Missing or invalid meeting details. Please provide:\n• Date (YYYY-MM-DD, tomorrow, next monday)\n• Time (HH:MM or 3 PM)\n• Participant emails\n• Optional: agenda and duration",
                success=False,
                error_code="INVALID_DETAILS"
            )
        
        # Validate date is not in the past
        meeting_datetime = datetime.strptime(f"{details.date} {details.time}", "%Y-%m-%d %H:%M")
        if meeting_datetime < datetime.now():
            return MeetingResponse(
                message="❌ Cannot book meetings in the past",
                success=False,
                error_code="PAST_DATE"
            )
        
        # Here you would integrate with a real calendar API
        message = f"✅ Meeting booked successfully!\n\n📅 Date: {details.date}\n🕐 Time: {details.time}\n👥 Participants: {', '.join(details.participants)}\n⏱️ Duration: {details.duration} minutes"
        
        if details.agenda:
            message += f"\n📋 Agenda: {details.agenda}"
        
        return MeetingResponse(message=message, details=details)
        
    except Exception as e:
        logger.error(f"Error in book_meeting_endpoint: {e}")
        return MeetingResponse(
            message=f"❌ An error occurred while booking the meeting: {str(e)}",
            success=False,
            error_code="INTERNAL_ERROR"
        )

@app.post("/chat")
async def chat(payload: ChatInput):
    """Enhanced chat endpoint with better error handling"""
    try:
        user_input = payload.user_input.lower().strip()
        
        # Check for meeting booking intent
        booking_keywords = ['book', 'schedule', 'arrange', 'set up', 'create']
        meeting_keywords = ['meeting', 'appointment', 'call', 'session']
        
        is_booking_request = any(keyword in user_input for keyword in booking_keywords) and \
                           any(keyword in user_input for keyword in meeting_keywords)
        
        if is_booking_request:
            details = extract_meeting_details(payload.user_input)
            if not details:
                return {
                    "response": "I'd be happy to help you book a meeting! Please provide:\n\n• **Date**: When would you like to meet? (e.g., tomorrow, 2025-01-15, next monday)\n• **Time**: What time works for you? (e.g., 3 PM, 15:30)\n• **Participants**: Who should be invited? (email addresses)\n• **Optional**: Meeting agenda and duration"
                }
            
            # Validate the meeting details
            meeting_datetime = datetime.strptime(f"{details.date} {details.time}", "%Y-%m-%d %H:%M")
            if meeting_datetime < datetime.now():
                return {"response": "❌ I can't book meetings in the past. Please choose a future date and time."}
            
            message = f"✅ Meeting booked successfully!\n\n📅 **Date**: {details.date}\n🕐 **Time**: {details.time}\n👥 **Participants**: {', '.join(details.participants)}\n⏱️ **Duration**: {details.duration} minutes"
            
            if details.agenda:
                message += f"\n📋 **Agenda**: {details.agenda}"
            
            return {"response": message}
        
        # Handle other conversation with the agent
        try:
            from app.agent import agent_executor
            reply = agent_executor.invoke({
                "input": payload.user_input,
                "chat_history": payload.chat_history
            })
            
            if isinstance(reply, dict):
                reply = reply.get("output") or reply.get("response") or str(reply)
            
            return {"response": reply}
            
        except ImportError:
            return {"response": "I'm here to help you book meetings! Just let me know when you'd like to schedule something."}
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {"response": f"I encountered an issue processing your request. Please try again or rephrase your message."}
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return {"response": "I'm having trouble processing your request right now. Please try again in a moment."}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to TailorTalk API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "Chat with the AI assistant",
            "/book_meeting": "Book a meeting directly",
            "/health": "Health check",
            "/docs": "API documentation"
        }
    }