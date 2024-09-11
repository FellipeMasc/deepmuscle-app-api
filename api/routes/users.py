import uuid
from typing import Any
import crud 
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select
from sql import database, models, schemas
from api.deps import SessionDep

models.Base.metadata.create_all(bind=database.engine)
router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user(session: SessionDep) -> Any:
    """
    Create new user.
    """
    user_create = schemas.UserCreate(email="fellipe_spd", password="oihahai")
    user = crud.create_user(session=session, user=user_create)
    return user
