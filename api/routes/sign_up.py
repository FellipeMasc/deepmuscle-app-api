from fastapi import APIRouter, Response,status
from sql.models import Users
from sql.database import SessionLocal, engine
from sql.schemas import UserCreate, UserOut
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash,check_password_hash

signup_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

session = SessionLocal(bind=engine)

@signup_router.post("/sign_up", response_model=UserOut, 
status_code=status.HTTP_201_CREATED)
async def sign_up(user: UserCreate):
    db_email = session.query(Users).filter(Users.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already exists")
    new_user = Users(
        email=user.email,
        full_name=user.full_name,
        hashed_password=generate_password_hash(user.password),
        is_active=False
        )
    session.add(new_user)
    session.commit()
    return Response(status_code=201, content="User created successfully")
    



