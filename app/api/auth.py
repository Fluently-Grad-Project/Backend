from datetime import datetime, timedelta
import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from proj.app.performance.time_tracker import track_time
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import get_db
from app.database.models import UserData, UserRefreshToken, VerificationCode
from app.schemas.user_schemas import LoginRequest, PasswordResetRequest, UpdatePasswprdRequest, UserDataResponse
from app.services.user_service import authenticate_user, get_user_by_email, request_password_reset, verify_email
from app.core.auth_manager import create_access_token, create_refresh_token, decode_token, get_password_hash, verify_recaptcha
from app.main import limiter
from app.core.config import pwd_context

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/login")
@track_time
@limiter.limit("3/minute")
async def login(form_data: LoginRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        email = form_data.get("email")
        password = form_data.get("password")

        ## to-implement-the-api: '''https://www.google.com/recaptcha/api/siteverify'''
        # recaptcha_token = form_data.get("recaptcha_token")

        # if not verify_recaptcha(recaptcha_token):
        #     logger.warning(f"reCAPTCHA failed for {email}")
        #     return JSONResponse(status_code=400, content={"message": "Failed CAPTCHA validation"})

        user = authenticate_user(db, email, password)
        if not user:
            logger.warning(f"Failed login - no user: {email}")
            return JSONResponse(status_code=401, content={"message": "Invalid credentials"})


        if not user.is_verified:
            logger.warning(f"Failed login - unverified: {email}")
            return JSONResponse(status_code=403, content={"message": "Email not verified"})
        
        if not pwd_context.verify(password, user.hashed_password):
            user.failed_attempts += 1
            db.commit()

            if user.failed_attempts >= 5:
                user.is_locked = True
                logger.error(f"User locked due to failed attempts: {email}")
            db.commit()
            return JSONResponse(status_code=401, content={"message": "Invalid credentials"})

        
        user.is_active=True
        user.is_locked=False
        user.failed_attempts = 0
        db.commit()
        logger.info(f"User logged in: {email}")

        access_token = create_access_token(user=user)
        refresh_token = create_refresh_token(user=user)
        user_response = UserDataResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            gender=user.gender,
            email=user.email,
            full_name=f"{user.first_name} {user.last_name}",
            is_verified=user.is_verified,
            is_active=user.is_active
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": jsonable_encoder(user_response)
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request. Please try again later")
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later"
        )

@router.get("/verify-email")
def verify_email_route(email: str, code: str, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        verification_code=db.query(VerificationCode).filter(VerificationCode.user_id==user.id,VerificationCode.code==code).first()
        if not verification_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
        if verification_code.expiry_time<datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired")
        user.is_verified=True
        db.delete(verification_code)
        db.commit()
        return {"message": "Email verified successfully."}
    except SQLAlchemyError as e:
        logger.error(f"Database error during email verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error during email verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
    
#for forget password service
@router.post("/request-password-reset")
@limiter.limit("1/minute")
def request_password_reset_route(req: PasswordResetRequest, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email(db, req.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        code = request_password_reset(db, user)
        return {"message": "Password reset code generated successfully", "code": code}
    except SQLAlchemyError as e:
        logger.error(f"Database error during password reset request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error during password reset request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
    

@router.post("/reset-password")
@limiter.limit("3/minute")
def reset_password_route(req: UpdatePasswprdRequest, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email(db, req.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        verification_code = db.query(VerificationCode).filter(
            VerificationCode.user_id == user.id,
            VerificationCode.code == req.code
        ).first()
        
        if not verification_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
        
        if verification_code.expiry_time < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired")
        
        user.hashed_password = get_password_hash(req.new_password)
        db.delete(verification_code)
        db.commit()
        
        return {"message": "Password reset successfully"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
    


@router.post("/refresh-token")
@limiter.limit("2/minute")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token, "Refresh")
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    db_token = db.query(UserRefreshToken).filter_by(refresh_token=refresh_token).first()

    if not db_token or db_token.is_used or db_token.is_revoked or db_token.expiry_time < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Refresh token is invalid or expired")

    user = db.query(UserData).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # db_token.is_used = True       ##marks the old token as used to prevent token-reuse - TBI

    new_access_token = create_access_token(user=user)
    new_refresh_token = create_refresh_token(user=user)

    new_token = UserRefreshToken(
        user_id=user.id,
        refresh_token=new_refresh_token,
        jwt_id=payload.get("jti"),
        expiry_time=datetime.utcnow() + timedelta(days=7)
    )

    db.add(new_token)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }