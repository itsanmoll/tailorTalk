import os
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent , AgentType
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.prompts import MessagesPlaceholder
from langchain_core.prompts.chat import ChatPromptTemplate
from app.calendarUtils import check_availability, book_event, book_event_from_text
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from pytz import timezone
from app.calendarUtils import book_event

load_dotenv()


# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     google_api_key=os.getenv("GOOGLE_API_KEY")
# )
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="meta-llama/llama-4-scout-17b-16e-instruct"  # or "llama3-70b-8192" or "gemma-7b-it"
)

tools = [
    # Tool(
    #     name="CheckCalendar",
    #     func=check_availability,
    #     description="Check calendar availability between two datetime ranges"
    # ),
    Tool(
        name="BookEvent",
        func=book_event_from_text,
        description=(
            "Use this tool to book a Google Calendar meeting. "
            "The user must provide ALL of the following in their message: "
            "event name (e.g. 'Interview with Meta'), date (YYYY-MM-DD), time (HH:MM 24hr), and duration (in minutes)."
            )
        )
]
# prompt = ChatPromptTemplate.from_messages([
#     ("system", 
#      "You are TailorTalk, an AI assistant that books meetings on Google Calendar for users. "
#      "Ask follow-up questions to collect any missing information like event name, day/date, time, and duration. "
#      "Once you have all details, use the BookEvent tool."
#      "Do not say you cannot book real-world events — you can book meetings using the BookEvent tool"),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("human", "{input}")
# ])
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    # agent_kwargs={"prompt": prompt}
)
