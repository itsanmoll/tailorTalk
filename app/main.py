from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import agent_executor

app = FastAPI()

class ChatInput(BaseModel):
    user_input: str

@app.post("/chat")
async def chat(payload: ChatInput):
    # reply = agent_executor.run(payload.user_input)
    reply = agent_executor.invoke({
    "input": payload.user_input,
    "chat_history": []  # or maintain history in-memory if needed
})
    return {"response": reply}
