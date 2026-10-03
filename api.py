from fastapi import FastAPI
from pydantic import BaseModel

from main import handle_request

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    return {"response": handle_request(req.message)}
