import enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Float, Date, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import JSON
from app.database.base import Base

Base = declarative_base()


class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class UserData(Base):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    gender = Column(Enum(GenderEnum))
    birth_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)

    matchmaking_attributes = relationship('MatchMaking', back_populates='user', uselist=False)
    activity_tracker = relationship('ActivityTracker', back_populates='user', uselist=False)
    user_manager = relationship('UserManager', back_populates='user_data', uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    sent_requests = relationship('FriendRequest', foreign_keys='FriendRequest.sender_id', back_populates='sender')
    received_requests = relationship('FriendRequest', foreign_keys='FriendRequest.receiver_id', back_populates='receiver')
    user_refresh_tokens = relationship('UserRefreshToken', back_populates='user')
    verification_codes = relationship('VerificationCode', back_populates='user')
    friends = relationship( "UserData", secondary="friendship", primaryjoin="UserData.id==Friendship.user_id", secondaryjoin="UserData.id==Friendship.friend_id", backref="friend_of")


class MatchMaking(Base):
    __tablename__ = 'matchmaking'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_data.id'))
    languages = Column(ARRAY(String))
    practice_frequency = Column(String)
    interests = Column(JSON)
    proficiency_level = Column(String)

    user = relationship('UserData', back_populates='matchmaking_attributes')


class ActivityTracker(Base):
    __tablename__ = 'activity_tracker'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_data.id'))
    streaks = Column(Integer)
    number_of_hours = Column(Integer)

    user = relationship('UserData', back_populates='activity_tracker')


class FriendRequestStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class FriendRequest(Base):
    __tablename__ = 'friend_requests'

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('user_data.id', ondelete='CASCADE'))
    receiver_id = Column(Integer, ForeignKey('user_data.id', ondelete='CASCADE'))
    status = Column(Enum(FriendRequestStatus), default=FriendRequestStatus.PENDING)
    sent_at = Column(DateTime, default=datetime.utcnow)


    sender = relationship('UserData', foreign_keys=[sender_id], back_populates='sent_requests')
    receiver = relationship('UserData', foreign_keys=[receiver_id], back_populates='received_requests')


class UserManager(Base):
    __tablename__ = 'user_manager'

    id = Column(Integer, primary_key=True, index=True)
    user_data_id = Column(Integer, ForeignKey('user_data.id', ondelete='CASCADE'), nullable=True)
    rating = Column(Float)

    user_data = relationship('UserData', back_populates='user_manager')


class Friendship(Base):
    __tablename__ = 'friendship'
    created_at = Column(DateTime, default=datetime.utcnow)


    user_id = Column(Integer, ForeignKey('user_data.id', ondelete='CASCADE'), primary_key=True)
    friend_id = Column(Integer, ForeignKey('user_data.id', ondelete='CASCADE'), primary_key=True)


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


class UserRefreshToken(Base):
    __tablename__ = 'user_refresh_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_data.id', ondelete='CASCADE'), nullable=False)
    refresh_token = Column(String, nullable=True)
    jwt_id = Column(String, nullable=True)
    is_used = Column(Boolean, default=False)
    is_revoked = Column(Boolean, default=False)
    added_time = Column(DateTime, default=datetime.utcnow)
    expiry_time = Column(DateTime)

    user = relationship('UserData', back_populates='user_refresh_tokens')


class TokenData(BaseModel):
    user_id: Optional[int] = None


class VerificationCode(Base):
    __tablename__ = 'verification_codes'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('user_data.id', ondelete='CASCADE'))
    expiry_time = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))

    user = relationship('UserData', back_populates='verification_codes')
