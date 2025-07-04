from pydantic import BaseModel, validator
from datetime import datetime
from app.database.models import ReportPriority  # Assuming this is where ReportPriority is defined
from typing import Optional


class ReportCreate(BaseModel):
    reported_user_id: int
    priority: ReportPriority  # This will now accept "CRITICAL"
    reason: str
 

    class Config:
        use_enum_values = True  # Crucial for proper serialization

class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    reported_user_id: int
    priority: ReportPriority
    reason: str
    created_at: datetime
    is_resolved: bool
    

  