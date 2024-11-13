from pydantic import BaseModel
from typing import Optional

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    hashed_password: str
    
class UserIn(BaseModel):
    full_name: str
    email: str

class UserCreate(UserIn):
    password: str

class UserDetailsCreate(BaseModel):
    height: float
    weight: float
    age: int
    fitness_level: str
    gender: str
    

class settings(BaseModel):
    authjwt_secret_key:str='efabc2443dbf72a23f7df4817d91ffeb035c99aca0bb5fd8e2b6cfca8e281892'

class Login(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True
        schemas_extra = {
            "example": {
                "email": "felipe@gmail.com",
                "password": "admin",
            }
        }


