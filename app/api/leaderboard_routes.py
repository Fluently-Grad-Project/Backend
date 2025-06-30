from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth_manager import get_current_user
from app.database.connection import get_db
from app.database.models import UserData
from app.schemas.leaderboard_schemas import LeaderboardUser
from app.services import leaderboard_service
from app.services.leaderboard_service import get_all_users_leaderboard

router = APIRouter()


@router.get("/all", response_model=List[LeaderboardUser])
def global_leaderboard(db: Session = Depends(get_db)):
    return get_all_users_leaderboard(db)

