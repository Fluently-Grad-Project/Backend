from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_schemas import UserDataCreate, UserDataResponse, RegisterResponse
from app.services.user_service import get_user_by_email, create_user, save_user
from app.core.auth_manager import create_access_token
from sqlalchemy.exc import SQLAlchemyError
import logging
from fastapi import BackgroundTasks
from app.services.email_service import send_verification_email
from app.core.config import BASE_URL
from sqlalchemy.orm import Session
from app.database.connection import get_db

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserDataCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already exists!"
            )        
        db_user, verification_code = create_user(db, user)

        verification_link = f"{BASE_URL}/auth/verify-email?email={db_user.email}&code={verification_code}"
        access_token = create_access_token(data={"sub": db_user.email})

        background_tasks.add_task(
            send_verification_email,
            email=db_user.email,
            verification_link=verification_link
        )

        return {
            "user": UserDataResponse.from_orm(db_user),
            "access_token": access_token,
            "verification_link": verification_link
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during registration: {str(e)}")