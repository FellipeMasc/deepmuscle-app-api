from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Union
from dotenv import load_dotenv
import jwt
import os
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from api.deps import SessionDep
from crud import get_user_by_email
from sql.schemas import UserOut

session = SessionDep()

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str | None = None   
    exp: int | None = None


def verify_password(plain_password, hashed_password):
    return plain_password == hashed_password
    # return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(session: Session, username: str, password: str):
    user = get_user_by_email(session=session, email=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(subject: str, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(reuseable_oauth)) -> UserOut:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenData(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: Union[dict[str, Any], None] = get_user_by_email(email=token_data.sub)


    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user
    