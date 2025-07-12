

# FastAPI backend for meeting booking bot
from typing import List, Tuple, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import re

app = FastAPI()

class MeetingDetails(BaseModel):
    date: str
    time: str
    participants: List[EmailStr]
    agenda: Optional[str] = None

class ChatInput(BaseModel):
    user_input: str
    chat_history: List[Tuple[str, str]] = []

class MeetingResponse(BaseModel):
    message: str
    details: Optional[MeetingDetails] = None

def extract_meeting_details(user_input: str) -> Optional[MeetingDetails]:
    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", user_input)
    time_match = re.search(r"\b(\d{1,2}:\d{2})\b", user_input)
    participants_match = re.findall(r"[\w\.-]+@[\w\.-]+", user_input)
    agenda_match = re.search(r"agenda[:\-]?\s*(.*)", user_input, re.IGNORECASE)
    if date_match and time_match and participants_match:
        return MeetingDetails(
            date=date_match.group(1),
            time=time_match.group(1),
            participants=participants_match,
            agenda=agenda_match.group(1) if agenda_match else None
        )
    return None

@app.post("/book_meeting", response_model=MeetingResponse)
async def book_meeting_endpoint(payload: ChatInput):
    details = extract_meeting_details(payload.user_input)
    if not details:
        raise HTTPException(status_code=400, detail="Missing or invalid meeting details. Please provide date (YYYY-MM-DD), time (HH:MM), and participant emails.")
    # Here you would integrate with a real calendar API
    message = f"Meeting booked on {details.date} at {details.time} with {', '.join(details.participants)}."
    if details.agenda:
        message += f" Agenda: {details.agenda}"
    return MeetingResponse(message=message, details=details)

@app.post("/chat")
async def chat(payload: ChatInput):
    user_input = payload.user_input.lower().strip()
    if "book" in user_input and "meeting" in user_input:
        details = extract_meeting_details(payload.user_input)
        if not details:
            return {"response": "Please provide date (YYYY-MM-DD), time (HH:MM), and participant emails to book a meeting."}
        message = f"Meeting booked on {details.date} at {details.time} with {', '.join(details.participants)}."
        if details.agenda:
            message += f" Agenda: {details.agenda}"
        return {"response": message}
    # ...existing code...
    try:
        reply = agent_executor.invoke({
            "input": payload.user_input,
            "chat_history": payload.chat_history
        })
        if isinstance(reply, dict):
            reply = reply.get("output") or reply.get("response") or str(reply)
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}