import json
from typing import Optional

import requests
from fastapi import APIRouter, Depends, FastAPI
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import FCMToken

SERVICE_ACCOUNT_FILE = (
    "app/Notification/fluentlytest-firebase-adminsdk-fbsvc-7018ac191b.json"
)
PROJECT_ID = "fluentlytest"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=[
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/firebase.messaging",
    ],
)

app = FastAPI()
router = APIRouter()


def get_access_token():
    """
    Get an access token for Firebase Cloud Messaging.
    """
    credentials.refresh(Request())
    print("Access Token:", credentials.token)  # Debugging line to check the token
    return credentials.token


class WordOfTheDayPayload(BaseModel):
    word: str
    parts_of_speech: str
    description: str
    example: str


class pushNotificationPayload(BaseModel):
    """
    Payload for push notifications.
    """

    title: str
    body: str
    token: str
    word_data: Optional[WordOfTheDayPayload] = None


@router.post("/send_notification")
def send_notification(payload: pushNotificationPayload):
    access_token = get_access_token()
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"
    message = {
        "message": {
            "token": payload.token,
            "notification": {
                "title": payload.title,
                "body": payload.body,
                "image": "https://i.postimg.cc/4yFQKt2k/fluently-high-resolution-logo-transparent.png",
            },
            "android": {
                "notification": {
                    "image": "https://i.postimg.cc/4yFQKt2k/fluently-high-resolution-logo-transparent.png",  # Android-specific image
                    "channel_id": "high_importance_channel",  # Required for Android 8+
                }
            },
            "apns": {  # iOS-specific
                "payload": {"aps": {"mutable-content": 1}},
                "fcm_options": {
                    "image": "https://i.postimg.cc/4yFQKt2k/fluently-high-resolution-logo-transparent.png"
                },
            },
            "webpush": {
                "notification": {
                    "icon": "https://i.postimg.cc/4yFQKt2k/fluently-high-resolution-logo-transparent.png",  # Add this line
                    "badge": "https://i.postimg.cc/4yFQKt2k/fluently-high-resolution-logo-transparent.png",  # Optional badge icon
                }
            },
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=json.dumps(message))
    return {"status_code": response.status_code, "response": response.json()}


@router.post("/send_word_notification")
def send_word_notification(token: str, word_data: WordOfTheDayPayload):
    access_token = get_access_token()
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    message = {
        "message": {
            "token": token,
            "notification": {
                "title": "📖 Word of the Day: " + word_data.word,
                "body": word_data.description,
                "image": "https://i.postimg.cc/4yFQKt2k/fluently-high-resolution-logo-transparent.png",
            },
            "data": {
                "type": "word_of_the_day",
                "word": word_data.word,
                "parts_of_speech": word_data.parts_of_speech,
                "description": word_data.description,
                "example": word_data.example,
            },
            "android": {
                "notification": {
                    "image": "https://i.postimg.cc/4yFQKt2k/fluently-high-resolution-logo-transparent.png",
                    "channel_id": "word_of_the_day_channel",  # Custom channel
                }
            },
            "apns": {
                "payload": {
                    "aps": {
                        "mutable-content": 1,
                        "category": "WORD_OF_THE_DAY",  # Custom iOS category
                    }
                }
            },
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=json.dumps(message))
    return response.json()


@router.get("/register_fcm_token")
def register_fcm_token(token: str, db: Session = Depends(get_db)):
    existing = db.get(FCMToken, token)
    if not existing:
        db.add(FCMToken(token=token))
        db.commit()
    return {"status": "active"}
