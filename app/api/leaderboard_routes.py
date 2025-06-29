from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth_manager import get_current_user
from app.database.connection import get_db
from app.database.models import UserData
from app.schemas.leaderboard_schemas import LeaderboardResponse
from app.services import leaderboard_service
from app.services.leaderboard_service import get_all_users_leaderboard

router = APIRouter()


@router.get("/all", response_model=List[LeaderboardResponse])
def global_leaderboard(db: Session = Depends(get_db)):
    return get_all_users_leaderboard(db)


@router.get("/friends", response_model=List[LeaderboardResponse])
def get_friends_leaderboard(
    db: Session = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
    page: int = Query(0, ge=0),
    page_size: int = Query(10, ge=1),
):
    db_result = leaderboard_service.get_friends_leaderboard(
        db=db, user_id=current_user.id, page=page, page_size=page_size
    )
    return [
        LeaderboardResponse(first_name=row[0], last_name=row[1], user_id=row[2], number_of_hours=row[3])
        for row in db_result
    ]
