from pydantic import BaseModel, Field
class UpdatePracticeHours(BaseModel):
    hours_to_add: int = Field(..., gt=0, description="Number of hours to add to the total")