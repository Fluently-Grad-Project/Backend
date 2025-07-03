from pydantic import BaseModel
from typing import Optional


class LeaderboardUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    profile_image: Optional[str]
    streaks: int
    minutes: int
    score: int

    class Config:
        from_attributes = True