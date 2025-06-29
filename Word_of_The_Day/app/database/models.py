from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.database.base import Base

# Base = declarative_base()


class WordOfTheDay(Base):
    __tablename__ = "word_of_the_day"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True)
    parts_of_speech = Column(String)
    description = Column(Text)
    example = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyWord(Base):
    __tablename__ = "daily_words"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    word_id = Column(Integer, ForeignKey("word_of_the_day.id"))
    word = relationship("WordOfTheDay")


class FCMToken(Base):
    __tablename__ = "fcm_tokens"

    token = Column(String, primary_key=True)  # FCM tokens are unique
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
