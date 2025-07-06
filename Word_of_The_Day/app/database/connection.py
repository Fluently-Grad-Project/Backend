from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:asdqwe123@localhost/WordOfTheDay"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
