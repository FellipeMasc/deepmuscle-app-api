from sqlalchemy.orm import Session, sessionmaker
from sql.database import engine, SessionLocal
from collections.abc import Generator
from typing import Annotated
from fastapi import Depends
from langserve.client import RemoteRunnable

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
SessionDep = Annotated[Session, Depends(get_db)]

def get_langserve() -> Generator[RemoteRunnable, None, None]:
    langserve = RemoteRunnable("http://127.0.0.1:8010/rag-conversation")
    yield langserve

        
LangserveDep = Annotated[RemoteRunnable, Depends(get_langserve)]