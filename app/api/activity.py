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
from datetime import datetime, timezone, timedelta


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
        update_streak(db, current_user)
         # For debugging
        activity_record.number_of_hours += hours_data.hours_to_add
        db.commit()
        db.refresh(activity_record)
    
        return activity_record
def update_streak(
      db:Session= Depends(get_db),
      current_user: UserData = Depends(get_current_user)
):
   activity_record = db.query(ActivityTracker).filter(ActivityTracker.user_id == current_user.id).first()
   if not activity_record:
         raise HTTPException(
              status_code=404,
              detail=f"Activity tracker record not found for user: {current_user.id}"
         )
   now = datetime.now(timezone.utc)
   if not activity_record.last_practiced_date:
        activity_record.streaks = 1
        activity_record.last_practiced_date = now
        db.commit()
        print(f"Streak updated to 1 day for user {current_user.id} to{activity_record.streaks} ")
        return 
   if activity_record.last_practiced_date.date()==now.date():
        print(f"User {current_user.id} has already practiced today. No streak update needed.")
        return 
   days_since_last = (now.date() - activity_record.last_practiced_date.date()).days
   if days_since_last == 1:
     activity_record.streaks += 1
     print(f"Streak updated for user {current_user.id} to {activity_record.streaks} days")
   else:
     activity_record.streaks = 1
     print(f"Streak reset for user {current_user.id} to 1 day")
   activity_record.last_practiced_date = now
   db.commit()

def reset_inactive_streaks(db: Session):
    """Resets streaks for users who didn't practice today."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    
    inactive_users = db.query(ActivityTracker).filter(
        ActivityTracker.last_practiced_date < yesterday.date()
    ).all()

    for user in inactive_users:
        user.streaks = 0 
    db.commit()
   
@router.get("/get_streaks") 
async def get_streaks(current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    activity_record = db.query(ActivityTracker).filter(
        ActivityTracker.user_id == current_user.id
    ).first()
    if not activity_record:
        raise HTTPException(
            status_code=404,
            detail=f"Activity tracker record not found for user: {current_user.id}"
        )
    return {"streaks": activity_record.streaks}

@router.get("/get_practice_hours")
async def get_practice_hours(
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    activity_record = db.query(ActivityTracker).filter(
        ActivityTracker.user_id == current_user.id
    ).first()
    
    if not activity_record:
        raise HTTPException(
            status_code=404,
            detail=f"Activity tracker record not found for user: {current_user.id}"
        )
    
    return {"total_practice_hours": activity_record.number_of_hours}     











