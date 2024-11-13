from fastapi import Depends
from sqlalchemy.orm import Session
from sql.database import SessionLocal, engine
from sql import models, schemas

# def create_user(session: Session, user: schemas.UserCreate):
#     db_obj = models.User(email="fellipe", full_name="abc3", hashed_password="abc")
#     session.add(db_obj)
#     session.commit()
#     session.refresh(db_obj)
#     return db_obj
session = SessionLocal(bind=engine)

def get_user(user_id: int):
    return session.query(models.Users).filter(models.Users.id == user_id).first()

def get_user_by_email(email: str):
    return session.query(models.Users).filter(models.Users.email == email).first()

