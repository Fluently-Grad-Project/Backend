from pydantic import BaseModel
from typing import Optional
from datetime import date

class FriendDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    profile_image: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    is_active: bool
    is_locked:bool

    class Config:
        from_attributes = True