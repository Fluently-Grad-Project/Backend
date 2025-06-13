import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_manager import get_current_user
from app.database.connection import get_db
from app.database.models import UserData
from app.schemas.user_schemas import MatchedUserResponse
from app.services.user_recommendation_service import get_similar_users_details

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/get-matched-users", response_model=List[MatchedUserResponse])
async def get_matched_users_endpoint(
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_db),
    n_recommendations: int = 5,
):
    return get_similar_users_details(
        user_id=current_user.id, db=db, n_recommendations=n_recommendations
    )
