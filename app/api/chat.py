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


# globals for connections
user_connections = {}              # user_id -> WebSocket (for signaling)
voice_rooms = defaultdict(set)    # room_id -> Set[WebSocket] (for voice data)
active_calls = {}                 # room_id -> (caller_id, callee_id)
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

@router.websocket("/ws/start_voice_chat/{room_id}")
async def voice_chat(websocket: WebSocket, room_id: str, user=Depends(get_current_user_ws)):
    parts = active_calls.get(room_id)
    if not parts or user.id not in parts:
        await websocket.close()
        return
    await websocket.accept()
    voice_rooms[room_id][user.id] = websocket
    print("VoiceChat joined:", user.id)
    try:
        while True:
            data = await websocket.receive_bytes()
            if data == b"END_CALL":
                for pid, ws in voice_rooms[room_id].items():
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

@router.post("/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    tmp = f"temp_audio/{uuid.uuid4()}"
    os.makedirs(tmp, exist_ok=True)
    in_path = f"{tmp}/{file.filename}"
    out_wav = f"{tmp}/{uuid.uuid4()}.wav"
    with open(in_path, "wb") as f:
        f.write(await file.read())
    try:
        subprocess.run(["ffmpeg", "-y", "-i", in_path, "-ar", "16000", "-ac", "1", out_wav], check=True)
        detector = get_hate_detector()
        text = detector.transcribe(out_wav)
        label = detector.predict(text)
        return {"transcript": text, "label": label}
    except subprocess.CalledProcessError:
        raise HTTPException(400, "Conversion failed")
    finally:
        for p in [in_path, out_wav]:
            if os.path.exists(p): os.remove(p)
        if os.path.exists(tmp): os.rmdir(tmp)