import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:12345678@localhost/fluently"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# to only create tables during local/dev environments
if os.getenv("ENV") != "production":
    Base.metadata.create_all(bind=engine)
