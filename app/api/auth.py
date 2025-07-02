import logging
from datetime import datetime, timedelta
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder

from app.core.exceptions import InvalidTokenError, InvalidTokenTypeError, TokenExpiredError
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.auth_manager import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.database.connection import get_db
from app.database.models import UserData, UserRefreshToken, VerificationCode, ActivityTracker
from app.performance.time_tracker import track_time
from app.schemas.user_schemas import (
    LoginRequest,
    PasswordResetRequest,
    UpdatePasswprdRequest,
    UserDataResponse,
)
from app.services.user_service import (
    authenticate_user,
    get_user_by_email,
    request_password_reset,
)
from app.core.utils import _

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@router.post("/login")
@track_time
@limiter.limit("3/minute")
async def login(
    request: Request, form_data: LoginRequest = Body(...), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    # setup_gettext(detect_language(request))
    print("LOGIN ENDPOINT HIT")

    try:
        email = form_data.email
        password = form_data.password
        user = authenticate_user(db, email, password)
        if not email or not password:
            raise HTTPException(status_code=422, detail=_("Email and password are required"))
        


        if not user:
            logger.warning(f"Failed login - no user: {email}")
            raise HTTPException(status_code=404, detail=_("User not found"))
        
        activity = db.query(ActivityTracker).filter_by(user_id=user.id).first()
        if user.is_locked:
            logger.warning(f"Failed login - user locked: {email}")
            raise HTTPException(status_code=403, detail=_("User account is locked"))

        if not user.is_verified:
            logger.warning(f"Failed login - unverified: {email}")
            raise HTTPException(status_code=403, detail=_("Email not verified"))

        if not verify_password(password, user.hashed_password):
            user.failed_attempts = (user.failed_attempts or 0) + 1
            if user.failed_attempts >= 5:
                user.is_locked = True
                logger.error(f"User locked due to failed attempts: {email}")
            db.commit()
        
            raise HTTPException(status_code=401, detail=_("Invalid credentials"))

        user.is_active = True
        user.is_locked = False
        user.failed_attempts = 0
        db.commit()
        logger.info(f"User logged in: {email}")

        user_response = UserDataResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            gender=str(user.gender) if user.gender else None,
            email=user.email,
            full_name=f"{user.first_name} {user.last_name}",
            is_verified=user.is_verified,
            is_active=user.is_active,
            profile_image=user.profile_image,
            proficiency_level=user.matchmaking_attributes.proficiency_level,
            interests=(
                user.matchmaking_attributes.interests
                if user.matchmaking_attributes
                else None
            ),
            is_locked=user.is_locked,
            hate_count=user.hate_count,
        )

        access_token = create_access_token(user=user_response)
        refresh_token = create_refresh_token(user=user)
        
        new_refresh_token_entry = UserRefreshToken(
            user_id=user.id,
            refresh_token=refresh_token,
            jwt_id=uuid4().hex,
            is_used=False,
            is_revoked=False,
            expiry_time=datetime.utcnow() + timedelta(days=7)
        )

        db.add(new_refresh_token_entry)
        db.commit()
        activity = db.query(ActivityTracker).filter_by(user_id=user.id).first()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": jsonable_encoder(user_response),
        }
    except HTTPException as http_e:
        raise http_e
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=_("An error occurred while processing your request. Please try again later"),
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_("An unexpected error occurred. Please try again later"),
        )


@router.get("/verify-email")
def verify_email_route(email: str, code: str, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=_("User not found")
            )

        verification_code = (
            db.query(VerificationCode)
            .filter(VerificationCode.user_id == user.id, VerificationCode.code == code)
            .first()
        )
        if not verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("Invalid verification code"),
            )
        if verification_code.expiry_time < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("Verification code expired"),
            )
        user.is_verified = True
        db.delete(verification_code)
        db.commit()
        return {"message": _("Email verified successfully")}
    except HTTPException as http_e:
        raise http_e
    except SQLAlchemyError as e:
        logger.error(f"Database error during email verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_("An error occurred while processing your request. Please try again later"),
        )
    except Exception as e:
        logger.error(f"Unexpected error during email verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_("An unexpected error occurred. Please try again later"),
        )


@router.post("/request-password-reset")
@limiter.limit("2/minute")
def request_password_reset_route(
    request: Request, req: PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    try:
        user = get_user_by_email(db, req.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=_("User not found")
            )

        code = request_password_reset(background_tasks, db, user)
        return {"message": _("Password reset code generated successfully"), "code": code}
    except HTTPException as http_e:
        raise http_e
    except SQLAlchemyError as e:
        logger.error(f"Database error during password reset request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_("An error occurred while processing your request. Please try again later"),
        )
    except Exception as e:
        logger.error(f"Unexpected error during password reset request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_("An unexpected error occurred. Please try again later"),
        )


@router.post("/reset-password")
@limiter.limit("3/minute")
def reset_password_route(
    request: Request, req: UpdatePasswprdRequest, db: Session = Depends(get_db)
):
    try:
        user = get_user_by_email(db, req.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=_("User not found")
            )
        
        if not req.email:
            raise HTTPException(status_code=422, detail=_("Email is required"))

        if not req.new_password or len(req.new_password) < 6:
            raise HTTPException(status_code=422, detail=_("Password must be at least 8 characters, one uppercase, one lowercase, one special character"))

        verification_code = (
            db.query(VerificationCode)
            .filter(
                VerificationCode.user_id == user.id, VerificationCode.code == req.code
            )
            .first()
        )

        if not verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("Invalid verification code"),
            )

        if verification_code.expiry_time < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("Verification code expired"),
            )

        user.hashed_password = get_password_hash(req.new_password)
        db.delete(verification_code)
        db.commit()

        return {"message": _("Password reset successfully")}
    
    except HTTPException as http_e:
        raise http_e

    except SQLAlchemyError as e:
        logger.error(f"Database error during password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_("An error occurred while processing your request. Please try again later"),
        )
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_("An unexpected error occurred. Please try again later"),
        )


@router.post("/refresh-token")
@limiter.limit("2/minute")
def refresh_access_token(
    request: Request, refresh_token: str, db: Session = Depends(get_db)
):
    try:
        payload = decode_token(refresh_token, "Refresh")

        user_id_str = payload.get("sub")
        if not user_id_str or not user_id_str.isdigit():
            raise HTTPException(status_code=403, detail=_("Invalid refresh token"))

        user_id = int(user_id_str)

        db_token = db.query(UserRefreshToken).filter_by(refresh_token=refresh_token).first()
        if (
            not db_token
            or db_token.is_used
            or db_token.is_revoked
            or db_token.expiry_time < datetime.utcnow()
        ):
            raise HTTPException(
                status_code=403, detail=_("Refresh token is invalid or expired")
            )

        user = db.query(UserData).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=_("User not found"))

        user_response = UserDataResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            gender=str(user.gender) if user.gender else None,
            email=user.email,
            full_name=f"{user.first_name} {user.last_name}",
            is_verified=user.is_verified,
            is_active=user.is_active,
            profile_image=user.profile_image,
            interests=(
                user.matchmaking_attributes.interests
                if user.matchmaking_attributes
                else None
            ),
            is_locked=user.is_locked,
            hate_count=user.hate_count,
        )

        new_access_token = create_access_token(user=user_response)
        new_refresh_token = create_refresh_token(user=user)

        new_token = UserRefreshToken(
            user_id=user.id,
            refresh_token=new_refresh_token,
            jwt_id=payload.get("jti"),
            expiry_time=datetime.utcnow() + timedelta(days=7),
        )

        db.add(new_token)
        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except TokenExpiredError:
        raise HTTPException(status_code=401, detail=_("Refresh token expired"))
    except (InvalidTokenError, InvalidTokenTypeError):
        raise HTTPException(status_code=403, detail=_("Invalid refresh token"))
    except SQLAlchemyError as e:
        logger.error(f"Database error during refresh: {str(e)}")
        raise HTTPException(status_code=500, detail=_("Database error"))
    except Exception as e:
        logger.error(f"Unexpected error during refresh: {str(e)}")
        raise HTTPException(status_code=500, detail=_("Unexpected server error"))
