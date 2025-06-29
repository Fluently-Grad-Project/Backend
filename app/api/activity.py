import logging

from fastapi import (
    APIRouter,

    Depends,
    HTTPException,
    status,
    
)
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.report_service import  ReportService
from app.core.auth_manager import get_current_user
from app.database.models import UserData, ActivityTracker
from uuid import uuid4
from app.schemas.activityschema import UpdatePracticeHours


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()
@router.patch("/update_hours")
async def update_hours(
    hours_data: UpdatePracticeHours,
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
        activity_record = db.query(ActivityTracker).filter(
        ActivityTracker.user_id == current_user.id,
    ).first()
        if not activity_record:
         raise HTTPException(
            status_code=404,
            detail=f"Activity tracker record not found for this user: {current_user.id}",
        )
        if hours_data.hours_to_add <= 0:
         raise HTTPException(
            status_code=400,
            detail="Hours to add must be a positive integer"
        )
         # For debugging
        activity_record.number_of_hours += hours_data.hours_to_add
        db.commit()
        db.refresh(activity_record)
    
        return activity_record

   
    











