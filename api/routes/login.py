from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from sql.schemas import Login
from sql.models import Users
from api.deps import SessionDep
from api.auth.main import authenticate_user, create_access_token, Token
import os 
from sql.database import SessionLocal, engine
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from werkzeug.security import generate_password_hash,check_password_hash



ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))

login_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

session = SessionLocal(bind=engine)

@login_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    db_user = session.query(Users).filter(Users.email == form_data.username).first()
    if db_user and check_password_hash(db_user.hashed_password, form_data.password):
        access_token = create_access_token(subject=db_user.email)

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid Credentials")

@login_router.post("/refresh")
async def refresh_token(Authorize: AuthJWT = Depends()):
        try:
            Authorize.jwt_refresh_token_required()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please provide a valid refresh token")

        current_user = Authorize.get_jwt_subject()
    
        access_token = Authorize.create_access_token(subject=current_user)
        response={
        "access": access_token
         }
        return jsonable_encoder(response)
