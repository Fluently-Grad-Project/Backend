from pydantic import BaseModel, Field
from typing import Optional

class UpdatePracticeHours(BaseModel):
    hours_to_add: Optional[int]= Field(..., gt=0, description="Number of hours to add to the total")

    minutes: Optional[int] = Field(0, ge=0, lt=60, description="Minutes to add (0-59)")