import enum
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class BaseORM(DeclarativeBase):
    pass


class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ProficiencyLevel(enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    FLUENT = "Fluent"


class UserData(BaseORM):
    __tablename__ = "user_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(Enum(GenderEnum))
    birth_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    failed_attempts: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profile_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    blocked_user_ids: Mapped[list[int]] = mapped_column(
        MutableList.as_mutable(ARRAY(Integer)), default=list
    )

    matchmaking_attributes = relationship(
        "MatchMaking", back_populates="user", uselist=False
    )
    activity_tracker = relationship(
        "ActivityTracker", back_populates="user", uselist=False
    )
    user_manager = relationship(
        "UserManager",
        back_populates="user_data",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sent_requests = relationship(
        "FriendRequest", foreign_keys="FriendRequest.sender_id", back_populates="sender"
    )
    received_requests = relationship(
        "FriendRequest",
        foreign_keys="FriendRequest.receiver_id",
        back_populates="receiver",
    )
    user_refresh_tokens = relationship("UserRefreshToken", back_populates="user")
    verification_codes = relationship("VerificationCode", back_populates="user")
    friends = relationship(
        "UserData",
        secondary="friendship",
        primaryjoin="UserData.id==Friendship.user_id",
        secondaryjoin="UserData.id==Friendship.friend_id",
        backref="friend_of",
    )


class MatchMaking(BaseORM):
    __tablename__ = "matchmaking"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_data.id"))
    languages: Mapped[list[str]] = mapped_column(ARRAY(String))
    practice_frequency: Mapped[str] = mapped_column(String)
    interests: Mapped[dict] = mapped_column(JSON)
    proficiency_level: Mapped[ProficiencyLevel] = mapped_column(Enum(ProficiencyLevel))

    user = relationship("UserData", back_populates="matchmaking_attributes")


class ActivityTracker(BaseORM):
    __tablename__ = "activity_tracker"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_data.id"))
    streaks: Mapped[int] = mapped_column(Integer)
    number_of_hours: Mapped[int] = mapped_column(Integer)

    user = relationship("UserData", back_populates="activity_tracker")


class FriendRequestStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class FriendRequest(BaseORM):
    __tablename__ = "friend_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("user_data.id", ondelete="CASCADE")
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("user_data.id", ondelete="CASCADE")
    )
    status: Mapped[FriendRequestStatus] = mapped_column(
        Enum(FriendRequestStatus), default=FriendRequestStatus.PENDING
    )
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sender = relationship(
        "UserData", foreign_keys=[sender_id], back_populates="sent_requests"
    )
    receiver = relationship(
        "UserData", foreign_keys=[receiver_id], back_populates="received_requests"
    )


class UserManager(BaseORM):
    __tablename__ = "user_manager"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_data_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user_data.id", ondelete="CASCADE"), nullable=True
    )
    rating: Mapped[float] = mapped_column(Float)

    user_data = relationship("UserData", back_populates="user_manager")


class Friendship(BaseORM):
    __tablename__ = "friendship"

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_data.id", ondelete="CASCADE"), primary_key=True
    )
    friend_id: Mapped[int] = mapped_column(
        ForeignKey("user_data.id", ondelete="CASCADE"), primary_key=True
    )


class JwtSettings(BaseSettings):
    secret: str
    issuer: str
    audience: str
    validate_audience: bool = True
    validate_issuer: bool = True
    validate_lifetime: bool = True
    validate_issuer_signing_key: bool = True
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


class JwtAuthResult(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    username: str
    token_string: str
    expiration: datetime


class UserRefreshToken(BaseORM):
    __tablename__ = "user_refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_data.id", ondelete="CASCADE"), nullable=False
    )
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    jwt_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    added_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expiry_time: Mapped[datetime] = mapped_column(DateTime)

    user = relationship("UserData", back_populates="user_refresh_tokens")


class TokenData(BaseModel):
    user_id: Optional[int] = None


class VerificationCode(BaseORM):
    __tablename__ = "verification_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_data.id", ondelete="CASCADE"))
    expiry_time: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10)
    )

    user = relationship("UserData", back_populates="verification_codes")


class ChatMessage(BaseORM):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("user_data.id", ondelete="CASCADE")
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("user_data.id", ondelete="CASCADE")
    )
    message: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String, default="sent", nullable=False)

    sender = relationship("UserData", foreign_keys=[sender_id])
    receiver = relationship("UserData", foreign_keys=[receiver_id])


class UserRating(BaseORM):
    __tablename__ = "user_ratings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rater_id: Mapped[int] = mapped_column(ForeignKey("user_data.id"), nullable=False)
    ratee_id: Mapped[int] = mapped_column(ForeignKey("user_data.id"), nullable=False)
    rating: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("rater_id", "ratee_id", name="_unique_rater_ratee"),
    )

    rater = relationship("UserData", foreign_keys=[rater_id])
    ratee = relationship("UserData", foreign_keys=[ratee_id])
