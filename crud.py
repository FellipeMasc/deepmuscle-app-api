from api.deps import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from sql import models, schemas

def create_user(session: Session, user: schemas.UserCreate):
    db_obj = models.User(email="fellipe", full_name="abc3", hashed_password="abc")
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def get_user(session: Session, user_id: int):
    return session.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(session: Session, email: str):
    return session.query(models.User).filter(models.User.email == email).first()

