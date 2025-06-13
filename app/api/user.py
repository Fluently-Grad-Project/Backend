import logging

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from app.core.auth_manager import create_access_token
from app.core.config import BASE_URL
from app.database.connection import get_db
from app.schemas.user_schemas import RegisterResponse, UserDataCreate, UserDataResponse
from app.services.email_service import send_verification_email
from app.services.user_service import create_user, get_user_by_email
import os
from app.core.auth_manager import get_current_user
from app.database.models import UserData
import shutil
from uuid import uuid4

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
def register_user(
    background_tasks: BackgroundTasks,
    user: UserDataCreate = Body(...),
    db: Session = Depends(get_db),
):
    try:
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )
        db_user, verification_code = create_user(db, user)

        verification_link = f"{BASE_URL}/auth/verify-email?email={db_user.email}&code={verification_code}"
        access_token = create_access_token(user=db_user)
        db.commit()

        background_tasks.add_task(
            send_verification_email,
            email=db_user.email,
            verification_link=verification_link,
        )

        return {
            "user": UserDataResponse.from_orm(db_user),
            "access_token": access_token,
            "verification_link": verification_link,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred during registration: {str(e)}"
        )


UPLOAD_FOLDER = "uploads/profile_pics"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):
    user = db.query(UserData).filter(UserData.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in {"png", "jpg", "jpeg"}:
        raise HTTPException(status_code=400, detail="Invalid file format")

    filename = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.profile_image = filename
    db.commit()

    return {
        "message": "Profile picture uploaded successfully",
        "image_path": f"/uploads/profile_pics/{filename}",
    }
