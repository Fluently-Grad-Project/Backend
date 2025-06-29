import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.core.exceptions import InvalidTokenError, InvalidTokenTypeError, TokenExpiredError
import bcrypt

# import requests
from fastapi import Depends, HTTPException, Query, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from sqlalchemy.orm import Session

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)
from app.database.connection import get_db
from app.database.models import UserData
from app.schemas.user_schemas import UserDataResponse


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password_strength(password: str) -> bool:
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.match(pattern, password))


################
# def verify_recaptcha(token: str) -> bool:
#     secret_key = RECAPTCH_KEY
#     response = requests.post(
#         "https://www.google.com/recaptcha/api/siteverify",
#         data={"secret": secret_key, "response": token},
#     )
#     result = response.json()
#     return result.get("success", False)

def create_access_token(
    user: UserDataResponse, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = {
        "user_id": user.id,
        "email": user.email,
        "full_name": f"{user.first_name} {user.last_name}",
        "is_verified": user.is_verified,
        "type": "Access",
    }
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user: UserData, expires_delta: Optional[timedelta] = None) -> str:
    try:
        expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
        to_encode = {
            "sub": str(user.id),
            "user_id": user.id,
            "type": "Refresh",
            "exp": expire
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except ExpiredSignatureError:
        raise TokenExpiredError("Refresh token expired")
    except JWTError:
        raise InvalidTokenError("Invalid refresh token")




def decode_token(token: str, token_type: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != token_type:
            raise InvalidTokenTypeError("Token type mismatch")
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredError("Token expired")
    except JWTError:
        raise InvalidTokenError("Invalid token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserData:
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer Token" if token else "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if not isinstance(email, str):
            raise unauthorized_exc
    except JWTError:
        raise unauthorized_exc

    user = db.query(UserData).filter(UserData.email == email).first()
    if user is None:
        raise unauthorized_exc

    return user

async def get_current_user_ws(websocket: WebSocket, token: str = Query(...)) -> UserData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise ValueError("Missing user_id")
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    db = next(get_db())
    user = db.query(UserData).filter(UserData.id == user_id).first()
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=404, detail="User not found")

    return user