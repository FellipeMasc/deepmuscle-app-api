import uuid
from typing import Any, Union
import crud 
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlmodel import col, delete, func, select
#from sql import database, models, schemas
from sql.schemas import UserDetailsModel
from sql.models import UserDetails, Users
from api.deps import SessionDep
from sql.database import SessionLocal, engine
from fastapi.encoders import jsonable_encoder
from datetime import datetime

user_details_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


session = SessionLocal(bind=engine)
@user_details_router.post("/user_details", response_model=UserDetailsModel,
status_code=status.HTTP_200_OK)
async def get_user_details(details_user: UserDetailsModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
       detail="Invalid Token")
    
    current_user = Authorize.get_jwt_subject()
    
    user = session.query(Users).filter(Users.email == current_user).first()
    
    new_user_details = UserDetails(
        height=details_user.height,
        weight=details_user.weight,
        gender=details_user.gender,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        age=details_user.age,
        fitness_level=details_user.fitness_level
        )
    new_user_details.user = user
    session.add(new_user_details)
    session.commit()

    response={
        "id": new_user_details.id,
        "height": new_user_details.height,
        "weight": new_user_details.weight,
        "gender": new_user_details.gender,
        "age": new_user_details.age,
        "fitness_level": new_user_details.fitness_level,
        "update_at":  new_user_details.updated_at,
        "created_at": new_user_details.created_at
        }
    return jsonable_encoder(response)
    




