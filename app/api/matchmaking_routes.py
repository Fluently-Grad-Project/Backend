from datetime import datetime
import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.user_service import authenticate_user, get_user_by_email, request_password_reset, verify_email
from app.core.auth_manager import create_access_token, create_refresh_token, get_password_hash
from app.database.models import UserData,MatchMaking,UserManager  # Make sure this import path is correct
from app.core.auth_manager import get_current_user
from app.services.user_recommendation_service  import get_similar_users_details
from pydantic import BaseModel
from app.schemas.user_schemas import MatchedUserResponse
router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



router = APIRouter()
@router.get("/get-matched-users", response_model=List[MatchedUserResponse])
async def get_matched_users_endpoint(
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_db),
    n_recommendations: int = 5
):
    return get_similar_users_details(
        user_id=current_user.id,
        db=db,
        n_recommendations=n_recommendations
    )

   