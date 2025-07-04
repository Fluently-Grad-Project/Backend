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

from fastapi import Header
import bleach
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, WebSocket, WebSocketDisconnect, WebSocketException, status
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session

from app.core.auth_manager import decode_token, get_current_user, get_current_user_ws
from app.core.websocket_manager import manager
from app.database.connection import get_db
from app.database.models import ActivityTracker, ChatMessage, UserData
from app.schemas.chat_schemas import ChatMessageResponse, UserContact
from app.services.chat_service import mark_messages_as_delivered

import subprocess

router = APIRouter()

# hate_detector=HateSpeechDetector()

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


# globals for connections
user_connections = {}              # user_id -> WebSocket (for signaling)
voice_rooms = defaultdict(dict)    # room_id -> Set[WebSocket] (for voice data)
active_calls = {}                  # room_id -> (caller_id, callee_id)
# ------------------------------------------------------------------------------------------------

def generate_room_id():
    return str(uuid.uuid4())


@router.websocket("/ws/send_call_request")
async def signal_socket(websocket: WebSocket, user=Depends(get_current_user_ws)):
    await websocket.accept()
    user_connections[user.id] = websocket
    print("Signal: user connected", user.id)
    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            if event == "call_user":
                callee_id = data["callee_id"]
                rid = generate_room_id()
                active_calls[rid] = (user.id, callee_id)
                callee = user_connections.get(callee_id)
                if callee:
                    await callee.send_json({
                        "event": "incoming_call",
                        "from_user": {"id": user.id, "name": user.first_name},
                        "room_id": rid
                    })
            elif event == "call_response":
                rid = data["room_id"]
                accepted = data["accepted"]
                if rid in active_calls:
                    caller, callee = active_calls[rid]
                    ws = user_connections.get(caller)
                    event_name = "call_accepted" if accepted else "call_rejected"
                    if ws:
                        await ws.send_json({"event": event_name, "room_id": rid})
                    if not accepted:
                        active_calls.pop(rid)
    except WebSocketDisconnect:
        print("Signal: disconnected", user.id)
    finally:
        user_connections.pop(user.id, None)


# ============================================================================

@router.websocket("/ws/start_voice_chat/{room_id}")
async def voice_chat(websocket: WebSocket, room_id: str, user=Depends(get_current_user_ws)):
    await websocket.accept()

    parts = active_calls.get(room_id)
    if not parts or user.id not in parts:
        await websocket.close()
        return

    db = next(get_db())
    user_in_db = db.query(UserData).filter(UserData.id == user.id).first()
    if user_in_db and user_in_db.is_locked:
        await websocket.send_text("END_CALL")
        await websocket.close()
        return

    voice_rooms[room_id][user.id] = websocket
    print("VoiceChat joined:", user.id)
    try:
        while True:
            data = await websocket.receive_bytes()
            if data == b"END_CALL":
                for pid, ws in list(voice_rooms[room_id].items()):
                    if ws.application_state == WebSocketState.CONNECTED:
                        await ws.send_text("END_CALL")
                        await ws.close()
                break
            for pid, ws in voice_rooms[room_id].items():
                if pid != user.id:
                    await ws.send_bytes(data)
    except WebSocketDisconnect:
        pass
    finally:
        voice_rooms[room_id].pop(user.id, None)
        if not voice_rooms[room_id]:
            active_calls.pop(room_id, None)


@router.post("/notify-hate-speech")
async def notify_hate_speech(
    request: Request,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    if authorization is None or not authorization.startswith("Bearer "):
        return {"error": "Authorization header missing or invalid"}

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = decode_token(token, token_type="Access")
        user_id = payload.get("user_id")
        if user_id is None:
            return {"error": "Invalid token payload"}
    except Exception as e:
        return {"error": f"Token decode error: {str(e)}"}

    user = db.query(UserData).filter(UserData.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    data = await request.json()
    transcript = data.get("transcript")
    label = data.get("label")

    print(f"Hate/Offensive speech detected! Transcript: {transcript}, Label: {label}")
    print(f"Authorization token received for user_id: {user_id}")

    if label.lower() in ["hate", "offensive"]:
        user.hate_count = (user.hate_count or 0) + 1
        print(f"Updated hate count for user {user.id}: {user.hate_count}")

        to_remove = []
        for rid, participants in active_calls.items():
            if user.id in participants:
                print(f"Ending call in room {rid} due to policy violation.")
                if rid in voice_rooms:
                    for pid, ws in voice_rooms[rid].items():
                        if ws.application_state == WebSocketState.CONNECTED:
                            await ws.send_text("END_CALL")
                            await ws.close()
                    voice_rooms.pop(rid, None)
                to_remove.append(rid)

        for rid in to_remove:
            active_calls.pop(rid, None)

        if user.hate_count >= 3:
            user.is_locked = True
            print(f"User {user.id} has been locked for repeated hate speech")
            ws = user_connections.get(user.id)
            if ws and ws.application_state == WebSocketState.CONNECTED:
                await ws.send_json({
                    "event": "account_locked",
                    "message": "Your account has been locked due to repeated hate speech"
                })
                await ws.close()

    db.commit()
    return {"status": "notification received"}