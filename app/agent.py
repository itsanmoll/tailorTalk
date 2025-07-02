import os
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent , AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from app.calendarUtils import check_availability, book_event, book_event_from_text

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

tools = [
    Tool(
        name="CheckCalendar",
        func=check_availability,
        description="Check calendar availability between two datetime ranges"
    ),
    Tool(
        name="BookEvent",
        func=book_event_from_text,
        description="Only use this tool when the user provides complete event details: event name, start time, and duration."
    )
]

agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True
)
