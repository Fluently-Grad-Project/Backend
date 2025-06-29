from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database.models import ActivityTracker, Friendship, UserData


def get_all_users_leaderboard(db: Session, limit: int = 10):
    # current_user = db.query(UserData).get(current_user_id)
    # if not current_user:
    #     return []

    return (
        db.query(
            UserData.first_name,
            UserData.last_name,
            UserData.id,
            func.coalesce(ActivityTracker.number_of_hours, 0).label("number_of_hours"),
        )
        .outerjoin(ActivityTracker, UserData.id == ActivityTracker.user_id)
        .filter(
            UserData.is_locked == False,
        )
        .order_by(desc("number_of_hours"))
        .limit(limit)
        .all()
    )



# def get_friends_leaderboard(db: Session, user_id: int, page: int = 1, page_size: int = 10):
#     offset = (page - 1) * page_size

#     current_user = db.query(UserData).get(user_id)
#     blocked_ids = set(current_user.blocked_user_ids)

#     return (
#         db.query(
#             UserData.first_name,
#             UserData.last_name,
#             func.coalesce(ActivityTracker.number_of_hours, 0).label("number_of_hours"),
#         )
#         .outerjoin(ActivityTracker, UserData.id == ActivityTracker.user_id)
#         .filter(
#             UserData.id.in_(
#                 db.query(Friendship.friend_id).filter(Friendship.user_id == user_id)
#             ),
#             UserData.id.notin_(blocked_ids),
#             ~UserData.blocked_user_ids.any(user_id)
#         )
#         .order_by(desc("number_of_hours"))
#         .offset(offset)
#         .limit(page_size)
#         .all()
#     )