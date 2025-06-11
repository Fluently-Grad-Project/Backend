from app.database.models import ChatMessage
from sqlalchemy.orm import Session


def mark_messages_as_delivered(db: Session, receiver_id: int, sender_id: int):
    messages = db.query(ChatMessage).filter(
        ChatMessage.sender_id == sender_id,
        ChatMessage.receiver_id == receiver_id,
        ChatMessage.status == "sent"
    ).all()

    for message in messages:
        message.status = "delivered"
    
    db.commit()
