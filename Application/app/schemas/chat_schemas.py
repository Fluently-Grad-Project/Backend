from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatMessageResponse(BaseModel):
    sender_id: int
    receiver_id: int
    message: str
    timestamp: datetime
    status: Optional[str] = "sent"

    class Config:
        from_attributes = True


class UserContact(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True
