from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Tuple
from datetime import datetime, timedelta
import secrets

from app.core.auth_manager import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from app.database.models import MatchMaking, UserData, UserManager, VerificationCode
from app.schemas.user_schemas import UserDataCreate, UserDataResponse


class UserCreationError(Exception):
    pass


def generate_verification_code() -> str:
    return secrets.token_hex(16)


def save_verification_code(
    db: Session, user_id: int, code: str, expires_in_min: int = 30
) -> VerificationCode:
    db.query(VerificationCode).filter(VerificationCode.user_id == user_id).delete()
    verification = VerificationCode(
        code=code,
        user_id=user_id,
        expiry_time=datetime.utcnow() + timedelta(minutes=expires_in_min),
    )
    db.add(verification)
    return verification


def create_user(db: Session, user_data: UserDataCreate) -> Tuple[UserDataResponse, str]:
    hashed_password = get_password_hash(user_data.password)
    verification_code = generate_verification_code()
    db_user = UserData(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=hashed_password,
        gender=user_data.gender,
        birth_date=user_data.birth_date,
        is_verified=False,
    )
    db.add(db_user)
    db.flush()

    db.add(
        MatchMaking(
            user_id=db_user.id,
            languages=user_data.languages,
            practice_frequency=user_data.practice_frequency,
            proficiency_level=user_data.proficiency_level,
            interests=user_data.interests,
        )
    )
    db.add(UserManager(user_data_id=db_user.id))

    verification = save_verification_code(db, db_user.id, verification_code)
    return db_user, verification.code


def authenticate_user(db: Session, email: str, password: str) -> Optional[UserData]:
    user = db.query(UserData).filter(UserData.email == email).first()
    if user and verify_password(password, user.hashed_password):
        # print(user)
        return user
    return None


def get_user_by_email(db: Session, email: str) -> Optional[UserData]:
    return db.query(UserData).filter(UserData.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[UserData]:
    return db.query(UserData).filter(UserData.id == user_id).first()


def save_user(db: Session, user: UserData):
    db.add(user)
    db.commit()
    db.refresh(user)


def verify_email(db: Session, user: UserData, code: str):
    verification_code = (
        db.query(VerificationCode)
        .filter(VerificationCode.user_id == user.id, VerificationCode.code == code)
        .first()
    )

    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
        )

    user.is_verified = True
    db.delete(verification_code)
    save_user(db, user)


def request_password_reset(db: Session, user: UserData) -> str:
    code = generate_verification_code()
    with db.begin():
        save_verification_code(db, user.id, code, expires_in_min=15)
    return code
