from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, EmailStr, Field

from app.database.models import GenderEnum
from pydantic import Field, field_validator

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
    profile_image: Optional[str] = None
    interests: Optional[Union[List[str], dict]] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str  # EmailStr
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


class MatchedUserResponse(BaseModel):
    user_id: int
    username: str
    interests: List[str]
    rating: Optional[float]
    age: int
    gender: GenderEnum
    similarity_score: float

    class Config:
        orm_mode = True


class UserRatingCreate(BaseModel):
    rating: float = Field(..., ge=1, le=5)



class UserProfileResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    gender: Optional[str]  # Using string instead of enum for JSON compatibility
    birth_date: Optional[date]
    profile_image: Optional[str]
    is_verified: bool
    created_at: datetime
    languages: Optional[list[str]]
    practice_frequency: Optional[str]
    interests: Optional[list[str]] 
    proficiency_level: Optional[str]
    streaks: Optional[int]
    hours_practiced: Optional[int]
    rating: Optional[float]



class UpdateProfileRequest(BaseModel):
    first_name: str = Field(..., min_length=1)  
    last_name: str = Field(..., min_length=1)   
    gender: str = Field(..., min_length=1)      
    interests: List[str] = Field(..., min_length=1)  

    @field_validator('gender')
    def validate_gender(cls, v):
        valid_genders = {'male', 'female', 'other'}
        if v.lower() not in valid_genders:
            raise ValueError("Gender must be 'male', 'female', or 'other'")
        return v.lower()

    @field_validator('interests')
    def validate_interests(cls, v):
        if not all(isinstance(interest, str) and interest.strip() for interest in v):
            raise ValueError("All interests must be non-empty strings")
        return v

class UpdateProfileResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    gender: Optional[str]
    interests: List[str]
    message: str = "Profile updated successfully"
