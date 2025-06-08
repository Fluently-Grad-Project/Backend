from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.user_schemas import UserDataCreate, UserDataResponse, RegisterResponse
from app.services.user_service import get_user_by_email, create_user, save_user
from app.core.auth_manager import create_access_token
from sqlalchemy.exc import SQLAlchemyError
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserDataCreate, db: Session = Depends(get_db)):
    try:
        logger.info("BEGIN: Attempting to register a new user...")

        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            logger.warning(f"User with email {user.email} already exists.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already exists! Use another email!"
            )        
        db_user, verification_code=create_user(db, user)
        verification_link=f"http://localhost:8000/auth/verify-email?email={db_user.email}&code={verification_code.code}"
        logger.info(f"Verification link: {verification_link}")
        
        access_token=create_access_token(data={"sub": db_user.email})
        logger.info(f"COMMIT: User {db_user.email} created successfully with ID {db_user.id}.")
        return {
            "user": UserDataResponse.from_orm(db_user),
            "access_token": access_token,
            "verification_link": verification_link
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the user. Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
