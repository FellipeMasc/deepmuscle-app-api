from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    hashed_password: str
    full_name: str
    is_active:Optional[bool] 

class UserDetailsModel(BaseModel):
    height: float
    weight: float
    gender: str
    age: int
    fitness_level: str


    

class settings(BaseModel):
    authjwt_secret_key:str='efabc2443dbf72a23f7df4817d91ffeb035c99aca0bb5fd8e2b6cfca8e281892'

class Login(BaseModel):
    email: str
    password: str

    
        


