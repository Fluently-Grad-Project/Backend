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
    "app/Notification/wordoftheday-b5a90-firebase-adminsdk-fbsvc-e1814ae290.json"
    
)
PROJECT_ID = "wordoftheday-b5a90"
try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/firebase.messaging",
        ],
    )
    # Force a token refresh to verify credentials work
    credentials.refresh(Request())
    print("Successfully authenticated with service account")
except Exception as e:
    print(f"Failed to authenticate with service account: {str(e)}")
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
                "body": payload.body
            },
            "android": {
                "notification": {
   
                    "channel_id": "high_importance_channel",  # Required for Android 8+
                }
            },

            },
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


@router.post("/register_fcm_token")
def register_fcm_token(token: str, db: Session = Depends(get_db)):
    existing = db.get(FCMToken, token)
    if not existing:
        db.add(FCMToken(token=token))
        db.commit()
    return {"status": "active"}
