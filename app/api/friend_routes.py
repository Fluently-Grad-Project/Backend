from fastapi import APIRouter, Depends
from app.database.models import UserData
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services import friend_service
from app.core.auth_manager import get_current_user

router = APIRouter()

@router.post("/request/{receiver_id}")
def send_request(receiver_id: int, db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    return friend_service.send_friend_request(db, sender_id=current_user.id, receiver_id=receiver_id)


@router.post("/accept/{sender_id}")
def accept_request(sender_id: int, db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    return friend_service.accept_friend_request(db, receiver_id=current_user.id, sender_id=sender_id)


@router.post("/reject/{sender_id}")
def reject_request(sender_id: int, db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    return friend_service.reject_friend_request(db, receiver_id=current_user.id, sender_id=sender_id)


@router.get("/get-friend-requests")
def get_requests(db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    return friend_service.get_pending_requests(db, user_id=current_user.id)


@router.get("/get-rejected-requests")
def get_rejected(db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    return friend_service.get_rejected_requests(db, user_id=current_user.id)


@router.get("/get-friend-list")
def get_friend_list(db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    return friend_service.get_friends(db, user_id=current_user.id)