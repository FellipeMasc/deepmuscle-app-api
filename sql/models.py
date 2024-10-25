from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Text
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True, index=True)
    full_name = Column(String(50), index=True)
    password = Column(Text)
    age = Column(Integer, nullable=True)
    country = Column(String(10), nullable=True)
    phone = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    def __repr__(self):
        return f"User('{self.email}', '{self.full_name}')"
    
    



