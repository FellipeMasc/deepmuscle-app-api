from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
class UserCreate(UserBase):
    password: str
class User(UserBase):
    id: int
    is_active: bool
    email: str
    full_name: str
    
    class Config:
        from_attributes = True