import base64
import json
from operator import or_
import os
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
from app.database.models import ChatMessage, UserData
from app.models.nlp_model import HateSpeechDetector
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


#   ================================================    #
@router.websocket("/ws/start_voice_chat")
async def start_voice_chat(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None,
    user: UserData = Depends(get_current_user_ws),
):
    await websocket.accept()
    print(f"[AudioMonitor] Connected: {user.first_name}")

    TEMP_DIR = "temp_audio"
    os.makedirs(TEMP_DIR, exist_ok=True)

    buffer = b""

    try:
        while True:
            try:
                chunk = await websocket.receive_bytes()
                buffer += chunk

                file_id = str(uuid.uuid4())
                input_path = os.path.join(TEMP_DIR, f"{file_id}.opus")
                converted_path = os.path.join(TEMP_DIR, f"{file_id}_converted.wav")

                with open(input_path, "wb") as f:
                    f.write(buffer)
                buffer = b""

                subprocess.run([
                    r"C:\ffmpeg\ffmpeg.exe", "-y", "-i", input_path,
                    "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", converted_path
                ], check=True)

                text = hate_detector.transcribe(converted_path)
                label = hate_detector.predict(text)

                print(f"[{user.first_name}] Transcript: {text} → {label}")

                if label in ["Offensive", "Hate"]:
                    if label == "Hate":
                        user.hate_count += 1
                        if user.hate_count >= 3:
                            user.is_locked = "suspended"
                            await websocket.send_json({"action": "suspend", "reason": "hate speech"})
                        else:
                            await websocket.send_json({"action": "warn", "reason": "hate speech"})
                    else:
                        await websocket.send_json({"action": "warn", "reason": "offensive language"})
                    await websocket.close()
                    break

            except subprocess.CalledProcessError:
                await websocket.send_json({"error": "Failed to convert audio"})
            except Exception as e:
                await websocket.send_json({"error": f"Processing failed: {str(e)}"})
            finally:
                for p in [input_path, converted_path]:
                    if os.path.exists(p):
                        os.remove(p)

    except WebSocketDisconnect:
        print(f"[AudioMonitor] Disconnected: {user.first_name}")
    except Exception as e:
        print(f"Voice Chat Error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
