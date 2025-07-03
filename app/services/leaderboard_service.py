
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.auth_manager import get_password_hash, verify_password
from app.database.models import  UserData,  ActivityTracker
from app.schemas.leaderboard_schemas import LeaderboardUser

from app.services.email_service import send_verification_code_email, send_verification_email


def get_all_users_leaderboard(db: Session):
    """
    Get top 5 users based on score (streaks * 10 + hours) 
    Only includes active, non-locked accounts
    """
    leaderboard = (
        db.query(
            UserData.id,
            UserData.first_name,
            UserData.last_name,
            UserData.profile_image,
            ActivityTracker.streaks,
            ActivityTracker.number_of_minutes.label("minutes"),
            (ActivityTracker.streaks * 10 + ActivityTracker.number_of_minutes //60).label("score")
        )
        .join(ActivityTracker, UserData.id == ActivityTracker.user_id)
        .filter(
            UserData.is_locked == False,  
            UserData.is_verified == True  
        )
        .order_by(
    func.coalesce(ActivityTracker.streaks * 10 + ActivityTracker.number_of_minutes, 0).desc(),
    ActivityTracker.streaks.desc(),
    ActivityTracker.number_of_minutes.desc(),
    UserData.id.asc()
)

        .limit(5)
        .all()
    )

    return [
        LeaderboardUser(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            profile_image=user.profile_image,
            streaks=user.streaks,
            minutes=user.minutes ,  
            score=user.score
        )
        for user in leaderboard
    ]