from operator import or_
from typing import List
import bleach
from fastapi import APIRouter, HTTPException, WebSocket, Depends, Query
from app.core.websocket_manager import manager
from app.core.auth_manager import get_current_user, get_current_user_ws
from app.database.models import ChatMessage, UserData
from app.database.connection import get_db
from app.schemas.chat_schemas import ChatMessageResponse
from app.schemas.chat_schemas import UserContact
from app.services.chat_service import mark_messages_as_delivered
from sqlalchemy.orm import Session


router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_chat( websocket: WebSocket, token: str = Query(...), user: UserData = Depends(get_current_user_ws)):
    print("WebSocket connection attempted")

    db=next(get_db())
    await manager.connect(user.id, websocket)
    print(f"Connected user {user.id}")
    try:
        while True:
            data = await websocket.receive_json()
            receiver_id = data["receiver_id"]
            message = data["message"]
            
            if receiver_id == user.id:
                raise HTTPException(400, "You can't message yourself")

            message = bleach.clean(data["message"])
            chat=ChatMessage(
                sender_id=user.id,
                receiver_id=receiver_id,
                message=message,
                status="sent"
            )
            db.add(chat)
            db.commit()
            await manager.send_message( f"{user.first_name}: {message}", receiver_id)
            mark_messages_as_delivered(db=db, receiver_id=receiver_id, sender_id=user.id)
            await websocket.send_json({ "status": "delivered",
                                        "receiver_id": receiver_id})

    except Exception as e:
        print(f"Websocket Error: {e}")
    finally:
        manager.disconnect(user.id)


@router.get("/chat/history", response_model=List[ChatMessageResponse])
def get_chat_history( receiver_id: int, db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    messages = (
        db.query(ChatMessage)
        .filter(
            ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == receiver_id)) |
            ((ChatMessage.sender_id == receiver_id) & (ChatMessage.receiver_id == current_user.id))
        ).order_by(ChatMessage.timestamp).all()
    )
    return messages


@router.get("/chat/my-contacts", response_model=List[UserContact])
def get_chat_contacts( db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    #user IDs from messages where current_user is a sender or a receiver
    messages = db.query(ChatMessage).filter(
        or_(ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id)).all()

    user_ids = set()
    for msg in messages:
        if msg.sender_id != current_user.id:
            user_ids.add(msg.sender_id)
        if msg.receiver_id != current_user.id:
            user_ids.add(msg.receiver_id)

    users = db.query(UserData).filter(UserData.id.in_(user_ids)).all()
    return users

@router.post("/chat/mark-as-read/{sender_id}")
def mark_messages_as_read(sender_id: int, db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)):
    messages = db.query(ChatMessage).filter( ChatMessage.sender_id == sender_id, ChatMessage.receiver_id == current_user.id, ChatMessage.status.in_(["sent", "delivered"])).all()
    for message in messages:
        message.status = "read"
    
    db.commit()
    return {"message": "Messages marked as read"}