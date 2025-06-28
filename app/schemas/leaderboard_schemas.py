from pydantic import BaseModel


class LeaderboardResponse(BaseModel):
    first_name: str
    last_name: str
    id: int
    number_of_hours: int