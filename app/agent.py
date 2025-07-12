import os
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain.prompts import MessagesPlaceholder
from langchain_core.prompts.chat import ChatPromptTemplate
from app.calendarUtils import (
    check_availability, 
    book_event, 
    book_event_from_text,
    get_upcoming_events,
    cancel_event,
    get_calendar_info
)
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from pytz import timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize LLM
try:
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="meta-llama/llama-4-scout-17b-16e-instruct"
    )
    logger.info("✅ LLM initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize LLM: {e}")
    llm = None

# Enhanced tools with better descriptions and error handling
tools = [
    Tool(
        name="BookEvent",
        func=book_event_from_text,
        description=(
            "Use this tool to book a Google Calendar meeting. "
            "The user must provide ALL of the following in their message: "
            "event name/title, date (YYYY-MM-DD, tomorrow, next monday), time (HH:MM or 3 PM), "
            "and optionally duration (in minutes/hours) and participant emails. "
            "Example: 'Book a meeting about project review tomorrow at 3 PM for 1 hour with john@example.com'"
        )
    ),
    Tool(
        name="CheckAvailability",
        func=lambda x: "Use this to check if a specific time slot is available before booking",
        description=(
            "Check if a specific time slot is available in the calendar. "
            "Use this before booking to avoid conflicts. "
            "Provide date and time in the format: 'Check availability for 2025-01-15 14:00 to 15:00'"
        )
    ),
    Tool(
        name="GetUpcomingEvents",
        func=lambda x: get_upcoming_events(5),
        description=(
            "Get a list of upcoming events from the calendar. "
            "Useful for showing users their scheduled meetings. "
            "No input required - just call this tool to get recent events."
        )
    ),
    Tool(
        name="CancelEvent",
        func=lambda x: "Use this to cancel an existing meeting. Provide the event ID or meeting details.",
        description=(
            "Cancel an existing meeting or event. "
            "You'll need the event ID or specific meeting details to cancel. "
            "Use this when users want to cancel a previously booked meeting."
        )
    )
]

# Enhanced system prompt for better conversation flow
system_prompt = """You are TailorTalk, an intelligent AI assistant that helps users book and manage meetings on Google Calendar.

Your capabilities:
1. **Book Meetings**: You can book meetings with natural language input
2. **Check Availability**: You can check if time slots are available
3. **View Events**: You can show upcoming meetings
4. **Cancel Events**: You can cancel existing meetings
5. **General Help**: You can answer questions about calendar management

Key Guidelines:
- Always be helpful and conversational
- Ask follow-up questions if meeting details are incomplete
- Confirm details before booking to avoid errors
- Provide clear, formatted responses with emojis for better readability
- If a user wants to book a meeting, extract all necessary details and use the BookEvent tool
- If a user asks about their schedule, use the GetUpcomingEvents tool
- If a user wants to cancel a meeting, help them identify and cancel it

Example interactions:
- User: "I need to book a meeting tomorrow at 3 PM"
- You: "I'd be happy to help! I'll need a few more details to book your meeting. What's the meeting about, and who should be invited? Also, how long should the meeting be?"

- User: "Show me my upcoming meetings"
- You: "Let me check your calendar for upcoming events..."

Remember to be friendly, professional, and always confirm important details before taking actions."""

# Create the agent with enhanced configuration
try:
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        early_stopping_method="generate"
    )
    logger.info("✅ Agent initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize agent: {e}")
    agent_executor = None

def process_user_input(user_input: str, chat_history: list = None) -> str:
    """
    Process user input with enhanced error handling and fallback responses
    """
    if not agent_executor:
        return "I'm having trouble connecting to my AI services right now. Please try again later."
    
    try:
        # Check for common patterns that don't need the full agent
        user_lower = user_input.lower()
        
        # Greeting patterns
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "👋 Hello! I'm TailorTalk, your AI calendar assistant. I can help you book meetings, check your schedule, and manage your calendar. What would you like to do today?"
        
        # Help patterns
        if any(word in user_lower for word in ['help', 'what can you do', 'capabilities']):
            return """🤖 **I can help you with:**

📅 **Meeting Management**
• Book new meetings with natural language
• Check calendar availability
• View upcoming events
• Cancel existing meetings

💬 **Natural Conversation**
• Just tell me what you need in plain English
• I'll ask for any missing details
• I'll confirm everything before booking

**Examples:**
• "Book a meeting tomorrow at 3 PM about project review"
• "Show me my upcoming meetings"
• "I need to cancel my meeting with John"

What would you like to do?"""
        
        # Use the agent for more complex requests
        if chat_history:
            # Convert chat history to the format expected by the agent
            formatted_history = []
            for role, content in chat_history:
                if role == "user":
                    formatted_history.append(("human", content))
                else:
                    formatted_history.append(("assistant", content))
            
            result = agent_executor.invoke({
                "input": user_input,
                "chat_history": formatted_history
            })
        else:
            result = agent_executor.invoke({
                "input": user_input,
                "chat_history": []
            })
        
        # Extract response from result
        if isinstance(result, dict):
            response = result.get("output") or result.get("response") or str(result)
        else:
            response = str(result)
        
        # Clean up the response
        response = response.strip()
        if not response:
            response = "I'm not sure how to help with that. Could you please rephrase your request?"
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        return f"I encountered an issue processing your request. Please try again or rephrase your message. Error: {str(e)}"

def get_agent_status() -> dict:
    """
    Get the current status of the agent and its components
    """
    return {
        "llm_available": llm is not None,
        "agent_available": agent_executor is not None,
        "tools_count": len(tools),
        "model_name": "meta-llama/llama-4-scout-17b-16e-instruct" if llm else None
    }
