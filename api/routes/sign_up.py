from fastapi import APIRouter,status
from sql.models import Users
from sql.database import SessionLocal, engine
from sql.schemas import UserCreate
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime

signup_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

session = SessionLocal(bind=engine)

@signup_router.post("/sign_up", response_model=UserCreate, 
status_code=status.HTTP_201_CREATED)
async def sign_up(user: UserCreate):
    db_email = session.query(Users).filter(Users.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already exists")
    new_user = Users(
        email=user.email,
        full_name=user.full_name,
        hashed_password=generate_password_hash(user.hashed_password),
        is_active=user.is_active,
        created_at=datetime.now(),
        updated_at=datetime.now()
        )
    session.add(new_user)
    session.commit()
    return new_user
    



