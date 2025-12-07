from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional



class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    admin: Optional[bool] = False


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    admin: Optional[bool] = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    created_at: datetime
    admin: bool

    class Config:
        orm_mode = True
