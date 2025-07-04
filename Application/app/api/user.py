import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.auth_manager import create_access_token
from app.core.config import BASE_URL
from app.database.connection import get_db
from app.schemas.user_schemas import (
    RegisterResponse,
    UserDataCreate,
    UserDataResponse,
    UserRatingCreate,
    UserProfileResponse,
    UpdateProfileResponse,
    UpdateProfileRequest
)
from app.services.email_service import send_verification_email
from app.services.user_service import create_user, get_user_by_email,get_user_profile,update_user_profile
import os
from app.core.auth_manager import get_current_user
from app.database.models import UserData, UserRating,UserRefreshToken,UserManager
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
    # Check for existing user first
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    try:
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

    except HTTPException:
        # Re-raise HTTPExceptions (like 422 for validation errors)
        db.rollback()
        raise
    except Exception:
        # Handle all other exceptions (like DB errors)
        db.rollback()
        logger.exception("Database error during registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
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

    file_ext = file.filename.split(".")[-1].lower() if file.filename else []
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


@router.post("/rate-user/{user_a_id}")
def rate_user(
    user_a_id: int,
    rating_data: UserRatingCreate,
    db: Session = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):
    if current_user.id == user_a_id:
        raise HTTPException(status_code=400, detail="You cannot rate yourself")

    ratee = db.query(UserData).filter(UserData.id == user_a_id).first()
    if not ratee:
        raise HTTPException(status_code=404, detail="User to be rated not found")
    if ratee.is_locked:
        raise HTTPException(status_code=403, detail="User is locked and cannot be rated")

    existing_rating = (
        db.query(UserRating)
        .filter(
            UserRating.rater_id == current_user.id, UserRating.ratee_id == user_a_id
        )
        .first()
    )

    if existing_rating:
        existing_rating.rating = rating_data.rating
    else:
        new_rating = UserRating(
            rater_id=current_user.id, ratee_id=user_a_id, rating=rating_data.rating
        )
        db.add(new_rating)

    db.commit()


    ratings = db.query(UserRating).filter(UserRating.ratee_id == user_a_id).all()
    if ratings:
        average_rating = sum(r.rating for r in ratings) / len(ratings)
        

        user_manager = db.query(UserManager).filter(UserManager.user_data_id == user_a_id).first()
        if not user_manager:
            user_manager = UserManager(user_data_id=user_a_id, rating=average_rating)
            db.add(user_manager)
        else:
            user_manager.rating = average_rating
        
        db.commit()

    return {"message": "User rated successfully"}


@router.get("/rating/{user_id}")
def get_user_average_rating(user_id: int, db: Session = Depends(get_db)):
    ratings = db.query(UserRating).filter(UserRating.ratee_id == user_id).all()
    if not ratings:
        return {"user_id": user_id, "average_rating": None, "count": 0}

    average = sum(r.rating for r in ratings) / len(ratings)
    return {
        "user_id": user_id,
        "average_rating": round(average, 2),
        "count": len(ratings),
    }


@router.post("/block-user/{user_id_to_block}")
def block_user(
    user_id_to_block: int,
    db: Session = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):
    if current_user.id == user_id_to_block:
        raise HTTPException(status_code=400, detail="You cannot block yourself")

    blocked_user = db.query(UserData).filter(UserData.id == user_id_to_block).first()
    if not blocked_user:
        raise HTTPException(status_code=404, detail="User to block not found")
    if blocked_user.is_locked:
        raise HTTPException(status_code=403, detail="User is locked and cannot be blocked")

    if user_id_to_block in current_user.blocked_user_ids:
        raise HTTPException(status_code=409, detail="User already blocked")

    current_user.blocked_user_ids.append(user_id_to_block)
    # blocked_user.blocked_user_ids.append(current_user.id)

    db.commit()

    return {"message": f"You blocked user {user_id_to_block} successfully"}


@router.get("/blocked-users")
def get_blocked_users(
    db: Session = Depends(get_db), current_user: UserData = Depends(get_current_user)
):
    user = db.query(UserData).filter(UserData.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"blocked_user_ids": user.blocked_user_ids}

@router.get("/{user_id}/profile", response_model=UserProfileResponse)
def get_user_profilee(
    user_id: int,
    db: Session = Depends(get_db)
):
    profile = get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile
@router.patch("/update-profile", response_model=UpdateProfileResponse)
def update_profile(
    update_data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):
    
    try:
        
        updated_profile = update_user_profile(
            db=db,
            user_id=current_user.id,
            update_data=update_data
        )
        return updated_profile
    except HTTPException as he:
        
        raise he
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
@router.post("/logout")
def logout_user(
    db: Session = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):

    try:
       
        current_user.is_active = False
        
     
        db.query(UserRefreshToken).filter(
            UserRefreshToken.user_id == current_user.id,
            UserRefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        
        db.commit()
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
