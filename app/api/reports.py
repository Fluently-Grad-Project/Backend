import logging

from fastapi import (
    APIRouter,

    Depends,
    HTTPException,
    status,
    
)
from sqlalchemy.orm import Session

from app.core.auth_manager import create_access_token
from app.core.config import BASE_URL
from app.database.connection import get_db

from app.services.email_service import send_verification_email
from app.services.report_service import  ReportService
import os
from app.core.auth_manager import get_current_user
from app.database.models import UserData, UserRating
import shutil
from uuid import uuid4
from app.schemas.report_schema import ReportCreate, ReportResponse
from typing import Optional
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report_service = ReportService(db)
    try:
        report = report_service.create_report(
            reporter_id=current_user.id,
            reported_user_id=report_data.reported_user_id,
            priority=report_data.priority,
            reason=report_data.reason,
           
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# @router.get("/about/{user_id}", response_model=list[ReportResponse])
# async def get_reports_about_user(
#     user_id: int,
#     resolved: Optional[bool] = None,
#     db: Session = Depends(get_db)
# ):
#     report_service = ReportService(db)
#     return report_service.get_user_reports(user_id, resolved)

@router.get("/by/{user_id}", response_model=list[ReportResponse])
async def get_reports_by_user(
    user_id: int,
    resolved: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    report_service = ReportService(db)
    return report_service.get_reports_made_by_user(user_id, resolved)
@router.get("/myreports", response_model=list[ReportResponse])
async def get_my_reports(
    resolved: Optional[bool] = None,
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report_service = ReportService(db)
    return report_service.get_reports_made_by_user(current_user.id, resolved)