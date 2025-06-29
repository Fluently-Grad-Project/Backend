import secrets
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_manager import get_password_hash, verify_password
from app.database.models import MatchMaking, UserData, UserManager, VerificationCode,GenderEnum,ActivityTracker
from app.schemas.user_schemas import UserDataCreate, UserDataResponse,UserProfileResponse,UpdateProfileResponse,UpdateProfileRequest
import re

from app.services.email_service import send_verification_code_email, send_verification_email

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
        is_verified=False
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
    db.add(ActivityTracker(user_id=db_user.id, number_of_hours=0, streaks=0))

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
        is_locked=db_user.is_locked,
        hate_count=db_user.hate_count,
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


def request_password_reset(background_tasks: BackgroundTasks, db: Session, user: UserData) -> str:
    code = generate_verification_code()
    print("WE SENT THE EMAIL!!!!!!!!!!!!")
    save_verification_code(db, user.id, code, expires_in_min=15)
    background_tasks.add_task(
        send_verification_code_email,
        email=user.email,
        code=code
    )
    db.commit()
    return code

def validate_email_format(email: str) -> str:
    """Basic format check only - allows any domain during testing"""
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
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

def get_user_profile(db: Session, user_id: int) -> Optional[UserProfileResponse]:
    user = db.query(UserData).filter(UserData.id == user_id).first()
    if not user:
        return None
    
    matchmaking = user.matchmaking_attributes
    activity = user.activity_tracker
    rating = user.user_manager.rating if user.user_manager else None
    
    return UserProfileResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender.value if user.gender else None,
        birth_date=user.birth_date if isinstance(user.birth_date, date) else None,
        profile_image=user.profile_image,
        is_verified=user.is_verified,
        created_at=user.created_at,
        languages=matchmaking.languages if matchmaking else None,
        practice_frequency=matchmaking.practice_frequency if matchmaking else None,
        interests=matchmaking.interests if matchmaking else None,
        proficiency_level=matchmaking.proficiency_level.value if matchmaking else None,
        streaks=activity.streaks if activity else None,
        hours_practiced=activity.number_of_hours if activity else None,
        rating=rating
    )
def update_user_profile(
    db: Session, 
    user_id: int, 
    update_data: UpdateProfileRequest
) -> UpdateProfileResponse:


    user = db.query(UserData).filter(UserData.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    

    if update_data.first_name is not None:
        user.first_name = update_data.first_name
    if update_data.last_name is not None:
        user.last_name = update_data.last_name
    if update_data.gender is not None:
        try:
            user.gender = GenderEnum(update_data.gender.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid gender value. Must be 'male', 'female', or 'other'"
            )
    

    if update_data.interests is not None:
        matchmaking = db.query(MatchMaking).filter(MatchMaking.user_id == user_id).first()
        if matchmaking:
            matchmaking.interests = update_data.interests
        else:

            matchmaking = MatchMaking(
                user_id=user_id,
                interests=update_data.interests

            )
            db.add(matchmaking)
    if update_data.proficiency_level is not None:

       

        matchmaking = db.query(MatchMaking).filter(MatchMaking.user_id == user_id).first()
        if matchmaking:
            matchmaking.proficiency_level = update_data.proficiency_level
        else:
            matchmaking = MatchMaking(
                user_id=user_id,
                proficiency_level=update_data.proficiency_level
            )
            db.add(matchmaking)
    
    db.commit()
    db.refresh(user)
    

    matchmaking = db.query(MatchMaking).filter(MatchMaking.user_id == user_id).first()
    
    return UpdateProfileResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender.value if user.gender else None,
        interests=matchmaking.interests if matchmaking else [],
        proficiency_level=matchmaking.proficiency_level.value if matchmaking and matchmaking.proficiency_level else None,
        message="Profile updated successfully"
    )
