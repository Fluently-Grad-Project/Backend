from pydantic import BaseModel
from typing import Optional


class LeaderboardUser(BaseModel):
    first_name: str
    last_name: str
    profile_image: Optional[str]
    streaks: int
    hours: int
    score: int

    class Config:
        from_attributes = True