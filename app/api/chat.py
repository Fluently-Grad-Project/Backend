import base64
from collections import defaultdict
from datetime import datetime
import json
from operator import or_
import os
import shutil
import time
from typing import Annotated, List
import uuid

import bleach
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect, WebSocketException, status
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session

from app.core.auth_manager import get_current_user, get_current_user_ws
from app.core.websocket_manager import manager
from app.database.connection import get_db
from app.database.models import ActivityTracker, ChatMessage, UserData
from app.models.nlp_model import HateSpeechDetector, get_hate_detector
from app.schemas.chat_schemas import ChatMessageResponse, UserContact
from app.services.chat_service import mark_messages_as_delivered

import subprocess

router = APIRouter()

hate_detector=HateSpeechDetector()

@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None,
    user: UserData = Depends(get_current_user_ws),
):
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = next(get_db())

    await manager.connect(user.id, websocket)

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except Exception:
                await websocket.send_json({"error": "Invalid message format"})
                continue

            receiver_id = data.get("receiver_id")
            message = data.get("message")

            if not isinstance(receiver_id, int) or receiver_id <= 0:
                await websocket.send_json({"error": "Invalid or missing receiver_id"})
                continue

            if not isinstance(message, str) or not message.strip():
                await websocket.send_json({"error": "Message cannot be empty"})
                continue

            if receiver_id == user.id:
                await websocket.send_json({"error": "Cannot message yourself"})
                continue

            try:
                message = bleach.clean(message)

                chat = ChatMessage(
                    sender_id=user.id,
                    receiver_id=receiver_id,
                    message=message,
                    status="sent",
                )
                db.add(chat)
                db.commit()

                await manager.send_message(f"{user.first_name}: {message}", receiver_id)
                mark_messages_as_delivered(db=db, receiver_id=receiver_id, sender_id=user.id)

                await websocket.send_json({
                    "status": "delivered",
                    "receiver_id": receiver_id
                })

            except Exception as e:
                db.rollback()
                await websocket.send_json({"error": "Failed to send message", "details": str(e)})
    except WebSocketDisconnect:
        print(f"User {user.id} disconnected")
    except WebSocketException as ws_exc:
        print(f"WebSocket exception: {ws_exc}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    except Exception as e:
        print(f"Unexpected error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        manager.disconnect(user.id)


@router.get("/chat/history", response_model=List[ChatMessageResponse])
def get_chat_history(
    receiver_id: int,
    db: Session = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):
    if receiver_id == current_user.id:
        raise HTTPException(400, "Cannot get chat history with yourself")

    messages = (
        db.query(ChatMessage)
        .filter(
            ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == receiver_id))
            | ((ChatMessage.sender_id == receiver_id) & (ChatMessage.receiver_id == current_user.id))
        )
        .order_by(ChatMessage.timestamp)
        .all()
    )

    if not messages:
        raise HTTPException(404, "No messages found")

    return messages



@router.get("/chat/my-contacts", response_model=List[UserContact])
def get_chat_contacts(
    db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)
):
    messages = (
        db.query(ChatMessage)
        .filter(
            or_(
                ChatMessage.sender_id == current_user.id,
                ChatMessage.receiver_id == current_user.id,
            )
        )
        .all()
    )

    user_ids = {
        msg.sender_id if msg.sender_id != current_user.id else msg.receiver_id
        for msg in messages
        if msg.sender_id != msg.receiver_id
    }

    if not user_ids:
        return []

    users = db.query(UserData).filter(UserData.id.in_(user_ids)).all()
    return users


@router.post("/chat/mark-as-read/{sender_id}")
def mark_messages_as_read(
    sender_id: int,
    db: Session = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):
    if sender_id == current_user.id:
        raise HTTPException(400, "Cannot mark your own messages as read")

    try:
        messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.sender_id == sender_id,
                ChatMessage.receiver_id == current_user.id,
                ChatMessage.status.in_(["sent", "delivered"]),
            )
            .all()
        )

        if not messages:
            raise HTTPException(404, "No unread messages found")

        for message in messages:
            message.status = "read"
        db.commit()

        return {"message": "Messages marked as read"}

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to mark messages as read: {str(e)}")

#for websocket connections
voice_rooms = defaultdict(set)

@router.websocket("/ws/start_voice_chat/{room_id}")
async def voice_chat(
    websocket: WebSocket,
    room_id: str,
    token: Annotated[str | None, Query()] = None,
    user=Depends(get_current_user_ws),
):
    await websocket.accept()
    print(f"[VoiceChat] {user.first_name} joined room {room_id}")
    voice_rooms[room_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_bytes()

            if data == b"END_CALL":
                print(f"[VoiceChat] {user.first_name} ended the call in {room_id}")

                for peer in list(voice_rooms[room_id]):
                    if peer.application_state == WebSocketState.CONNECTED:
                        try:
                            await peer.send_text("END_CALL")
                            await peer.close()
                        except:
                            pass
                break  #exits the loop to disconnect this user

            #broadcast voice data
            for peer in voice_rooms[room_id]:
                if peer != websocket and peer.application_state == WebSocketState.CONNECTED:
                    try:
                        await peer.send_bytes(data)
                    except:
                        pass

    except WebSocketDisconnect:
        print(f"[VoiceChat] {user.first_name} disconnected from {room_id}")
    finally:
        voice_rooms[room_id].discard(websocket)
        print(f"[VoiceChat] Active sockets in {room_id}: {len(voice_rooms[room_id])}")