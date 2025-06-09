from datetime import datetime, timedelta
from typing import Any, Dict
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.database.connection import get_db
from sqlalchemy.orm import Session
from app.database.models import UserData
from app.core.config import SECRET_KEY, ALGORITHM, pwd_context, ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

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
    to_encode = {
        "sub": user.email,
        "user_id": user.id
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if "sub" in payload else None
    except jwt.JWTError:
        return None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer Token" if token else "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserData).filter(UserData.email == email).first()
    if user is None:
        raise credentials_exception

    return user
