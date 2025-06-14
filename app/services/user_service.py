import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_manager import get_password_hash, verify_password
from app.database.models import MatchMaking, UserData, UserManager, VerificationCode
from app.schemas.user_schemas import UserDataCreate, UserDataResponse
import re

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
    validate_email_format(user_data.email)
    validate_password_strength(user_data.password)
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

    user_response = UserDataResponse(
        id=db_user.id,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        email=db_user.email,
        full_name=f"{db_user.first_name} {db_user.last_name}",
        gender=str(db_user.gender) if db_user.gender else None,
        is_verified=db_user.is_verified,
        is_active=db_user.is_active,
        profile_image=db_user.profile_image,
        interests=(
            db_user.matchmaking_attributes.interests
            if db_user.matchmaking_attributes
            else None
        ),
    )
    return user_response, verification.code


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
def validate_email_format(email: str) -> str:
    """Basic format check only - allows any domain during testing"""
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):  # Simple: something@something.something
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email format (use test@test.test)"
        )
    return email.lower()  
def validate_password_strength(password: str) -> None:
    """
    Verify password meets strength requirements:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter  
    - At least 1 number
    - At least 1 special character
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long"
        )
    
    if not any(c.isupper() for c in password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one uppercase letter"
        )
        
    if not any(c.islower() for c in password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one lowercase letter"
        )
        
    if not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one number"
        )
        
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one special character"
        )
