from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from cachetools import TTLCache
from typing import Tuple, Dict, Any
from cachetools import cached

from app.database.models import FriendRequest, FriendRequestStatus, Friendship, UserData


def validate_user_exists(db: Session, user_id: int):
    user = db.query(UserData).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user

def validate_user_is_notSuspended(db: Session, user_id: int):
    user = db.query(UserData).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with ID {user_id} is suspended",
        )

        
    return user
def validate_not_self_request(sender_id: int, receiver_id: int):
    """Validate user isn't sending request to themselves"""
    if sender_id == receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send friend request to yourself",
        )


def validate_not_already_friends(db: Session, user1_id: int, user2_id: int):
    """Check if users are already friends"""
    existing_friendship = (
        db.query(Friendship)
        .filter(
            ((Friendship.user_id == user1_id) & (Friendship.friend_id == user2_id))
            | ((Friendship.user_id == user2_id) & (Friendship.friend_id == user1_id))
        )
        .first()
    )
    if existing_friendship:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Users are already friends"
        )


def send_friend_request(db: Session, sender_id: int, receiver_id: int):
    validate_not_self_request(sender_id, receiver_id)
    validate_user_exists(db, sender_id)
    validate_user_exists(db, receiver_id)
    validate_user_is_notSuspended(db, sender_id)
    validate_user_is_notSuspended(db, receiver_id)
    validate_not_already_friends(db, sender_id, receiver_id)

    existing_request = (
        db.query(FriendRequest)
        .filter(
            (
                (FriendRequest.sender_id == sender_id)
                & (FriendRequest.receiver_id == receiver_id)
            )
            | (
                (FriendRequest.sender_id == receiver_id)
                & (FriendRequest.receiver_id == sender_id)
            ),
            FriendRequest.status == FriendRequestStatus.PENDING,
        )
        .first()
    )

    if existing_request:
        if existing_request.sender_id == sender_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend request already sent",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This user has already sent you a friend request",
            )

    new_request = FriendRequest(
        sender_id=sender_id,
        receiver_id=receiver_id,
        status=FriendRequestStatus.PENDING,
        sent_at=datetime.utcnow(),
    )
    db.add(new_request)
    db.commit()
    return {"detail": "Friend request sent successfully"}


def accept_friend_request(db: Session, receiver_id: int, sender_id: int):
    validate_user_exists(db, sender_id)
    validate_user_exists(db, receiver_id)
    validate_user_is_notSuspended(db, sender_id)
    validate_user_is_notSuspended(db, receiver_id)
    validate_not_already_friends(db, sender_id, receiver_id)

    request = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.sender_id == sender_id,
            FriendRequest.receiver_id == receiver_id,
            FriendRequest.status == FriendRequestStatus.PENDING,
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending friend request found",
        )

    friendship1 = Friendship(
        user_id=receiver_id, friend_id=sender_id, created_at=datetime.utcnow()
    )
    friendship2 = Friendship(
        user_id=sender_id, friend_id=receiver_id, created_at=datetime.utcnow()
    )

    request.status = FriendRequestStatus.ACCEPTED
    request.sent_at = datetime.utcnow()

    db.add_all([friendship1, friendship2, request])
    db.commit()

    return {"detail": "Friend request accepted successfully"}


def reject_friend_request(db: Session, receiver_id: int, sender_id: int):
    validate_user_exists(db, sender_id)
    validate_user_exists(db, receiver_id)

    request = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.sender_id == sender_id,
            FriendRequest.receiver_id == receiver_id,
            FriendRequest.status == FriendRequestStatus.PENDING,
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending friend request found",
        )

    request.status = FriendRequestStatus.REJECTED
    request.sent_at = datetime.utcnow()
    db.commit()

    return {"detail": "Friend request rejected successfully"}


def get_pending_requests(db: Session, user_id: int) -> List[FriendRequest]:
    validate_user_exists(db, user_id)
    return (
        db.query(FriendRequest)
        .filter(
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == FriendRequestStatus.PENDING,
        )
        .all()
    )


def get_rejected_requests(db: Session, user_id: int) -> List[FriendRequest]:
    validate_user_exists(db, user_id)
    return (
        db.query(FriendRequest)
        .filter(
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == FriendRequestStatus.REJECTED,
        )
        .all()
    )


def get_friends(db: Session, user_id: int) -> List[UserData]:
    user = validate_user_exists(db, user_id)
    return db.query(UserData).join(
        Friendship,
        or_(
            (Friendship.user_id == user_id) & (Friendship.friend_id == UserData.id),
            (Friendship.friend_id == user_id) & (Friendship.user_id == UserData.id)
        )
    ).filter(
        UserData.is_locked == False
    ).all()
