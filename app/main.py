from typing import List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import agent_executor

app = FastAPI()

class ChatInput(BaseModel):
    user_input: str
    chat_history: List[Tuple[str, str]] = []

@app.post("/chat")
async def chat(payload: ChatInput):
    # if payload.user_input.lower().strip() in ["hi", "hello", "hey"]:
    #     return {"response": "👋 Hello! How can I help you schedule your meeting?"}
    try:
        reply= agent_executor.invoke({
            "input": payload.user_input,
            "chat_history": payload.chat_history
        })
        if isinstance(reply, dict):
            reply = reply.get("output") or reply.get("response") or str(reply)
        return {"response": reply}
    except Exception as e :
        return {"error" : str(e)}