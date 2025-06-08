from app.core.auth_manager import create_access_token, verify_password, get_password_hash
from sqlalchemy.orm import Session
from app.database.models import UserData, UserManager, VerificationCode
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime, timedelta
import secrets

from app.schemas.user_schemas import UserDataCreate

def create_user(db: Session, user_data: UserDataCreate):
    from app.core.auth_manager import get_password_hash

    hashed_password = get_password_hash(user_data.password)
    verification_code = generate_verification_code()
    
    db_user = UserData(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=hashed_password,
        gender=user_data.gender,
        is_verified=False
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        if not db_user.id:
            raise Exception("User ID was not generated correctly.")

        user_manager = UserManager(user_data_id=db_user.id)
        db.add(user_manager)
        db.commit()
        db.refresh(user_manager)

        verification = VerificationCode(
            code=verification_code,
            user_id=db_user.id,
            expiry_time=datetime.utcnow() + timedelta(minutes=30)
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)

        return db_user, verification

    except Exception as e:
        db.rollback()
        raise e


def authenticate_user(db: Session, email: str, password: str) -> Optional[UserData]:
    user = db.query(UserData).filter(UserData.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def generate_verification_code() -> str:
    return secrets.token_hex(16)

def get_user_by_email(db: Session, email: str) -> Optional[UserData]:
    return db.query(UserData).filter(UserData.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[UserData]:
    return db.query(UserData).filter(UserData.id == user_id).first()

def save_user(db: Session, user: UserData):
    db.add(user)
    db.commit()
    db.refresh(user)

def verify_email(db: Session, user: UserData, code: str):
    verification_code = db.query(VerificationCode).filter(VerificationCode.user_id == user.id, VerificationCode.code == code).first()
    if not verification_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
    user.is_verified = True
    db.delete(verification_code)
    save_user(db, user)

def request_password_reset(db: Session, user: UserData):
    code = generate_verification_code()
    verification_code = VerificationCode(code=code, user_id=user.id)
    db.add(verification_code)
    db.commit()
    return code
