from pydantic import BaseModel


class LeaderboardResponse(BaseModel):
    first_name: str
    last_name: str
    number_of_hours: int
