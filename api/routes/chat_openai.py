from fastapi import APIRouter, Depends, HTTPException
from api.deps import SessionDep, LangserveDep
from typing import Annotated
from pydantic import BaseModel
from sql.models import Users
from sql.database import SessionLocal, engine
from fastapi.responses import StreamingResponse
from internal.sse import EventSourceResponse
from langserve.api_handler import APIHandler
from langserve.callbacks import AsyncEventAggregatorCallback


session = SessionLocal(bind=engine)

chat_openai_router = APIRouter(
    prefix="/chat_openai",
    tags=["chat_openai"]
)


class InputMsg(BaseModel):
    question: str
    chat_history: list

async def get_streaming_openai(input: dict, langserve: LangserveDep):
    async for chunk in langserve.astream(input):
        yield chunk
        
@chat_openai_router.post("/chat", status_code=200)
async def chat_openai(input : InputMsg, langserve: LangserveDep) -> EventSourceResponse:    
    print(input)
    input_msg = {
        "question": "oi",
        "chat_history": [],
    }
    # return StreamingResponse(get_streaming_openai(input_msg, langserve), media_type="text/event-stream")
    return StreamingResponse(langserve.stream(input_msg), media_type="text/event-stream")