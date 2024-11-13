from fastapi import APIRouter, Depends, HTTPException
from api.auth.main import get_current_user
from api.deps import SessionDep, LangserveDep
from typing import Annotated
from pydantic import BaseModel
from sql.models import Users
from sql.database import SessionLocal, engine
from fastapi.responses import StreamingResponse

from sql.schemas import UserOut


session = SessionLocal(bind=engine)

chat_openai_router = APIRouter(
    prefix="/chat_openai",
    tags=["chat_openai"]
)


class InputMsg(BaseModel):
    question: str
    chat_history: list

# async def get_streaming_openai(input: dict, langserve: LangserveDep):
#     async for chunk in langserve.astream(input):
#         yield chunk
        
@chat_openai_router.post("/chat", status_code=200)
async def chat_openai(input_msg: str, user: UserOut = Depends(get_current_user)):
    print(user)
    return input_msg