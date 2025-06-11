from datetime import date
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    gender: Optional[str] = None

    class Config:
        from_attributes = True


class UserDataCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    gender: Optional[str] = None
    birth_date: date
    languages: List[str]
    proficiency_level: str
    practice_frequency: str
    interests: List[str]

class UserDataResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    gender: Optional[str]
    is_verified: bool
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str #EmailStr
    password: str

class RegisterResponse(BaseModel):
    user: UserDataResponse
    access_token: str
    verification_link: str

class PasswordResetRequest(BaseModel):
    email: str

class UpdatePasswprdRequest(BaseModel):
    email: str
    new_password: str
    code: str