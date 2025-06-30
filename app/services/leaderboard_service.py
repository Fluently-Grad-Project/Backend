
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
            UserData.first_name,
            UserData.last_name,
            UserData.profile_image,
            ActivityTracker.streaks,
            ActivityTracker.number_of_hours.label("hours"),
            (ActivityTracker.streaks * 10 + ActivityTracker.number_of_hours).label("score")
        )
        .join(ActivityTracker, UserData.id == ActivityTracker.user_id)
        .filter(
            UserData.is_locked == False,  
            UserData.is_verified == True  
        )
        .order_by(func.coalesce(ActivityTracker.streaks * 10 + ActivityTracker.number_of_hours, 0).desc())
        .limit(5)
        .all()
    )

    return [
        LeaderboardUser(
            first_name=user.first_name,
            last_name=user.last_name,
            profile_image=user.profile_image,
            streaks=user.streaks,
            hours=user.hours,
            score=user.score
        )
        for user in leaderboard
    ]