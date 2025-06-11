from datetime import datetime, timedelta
import re
from typing import Any, Dict
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Query, WebSocket, requests, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.database.connection import get_db
from sqlalchemy.orm import Session
from app.database.models import UserData
from app.core.config import SECRET_KEY, ALGORITHM, pwd_context, ACCESS_TOKEN_EXPIRE_MINUTES, RECAPTCH_KEY


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def verify_password_strength(password: str) -> bool:
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.match(pattern, password))


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

################
def verify_recaptcha(token: str) -> bool:
    secret_key = RECAPTCH_KEY
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": secret_key, "response": token}
    )
    result = response.json()
    return result.get("success", False)



def create_access_token(user: UserData, expires_delta: timedelta = None) -> str:
    to_encode = {
        # "sub": user,
        "user_id": user.id,
        "email": user.email,
        "full_name": f"{user.first_name} {user.last_name}",
        "is_verified": user.is_verified
    }
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user: UserData, expires_delta: timedelta = None):
    try:
        to_encode = {
            "sub": user.email,
            "user_id": user.id
        }
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


def decode_token(token: str, token_type:str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if "sub" in payload else None
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail=f"{token_type} Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail=f"Invalid {token_type} token")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    e = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer Token" if token else "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise e
    except JWTError:
        try:
            payload = jwt.get_unverified_claims(token)
            user_id = payload.get("sub")
            if user_id:
                user = db.query(UserData).get(user_id)
                if user:
                    user.is_active = False
                    db.commit()
        except:
            pass
        
        raise e

    user = db.query(UserData).filter(UserData.email == email).first()
    if user is None:
        raise e

    return user


async def get_current_user_ws(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise ValueError()
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    db = next(get_db())
    user = db.query(UserData).filter(UserData.id == user_id).first()
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=404, detail="User not found")

    return user