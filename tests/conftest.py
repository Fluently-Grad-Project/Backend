import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.database.connection import BaseORM
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def db_session():
    """Create a database session using GitHub's PostgreSQL service"""
    # Use GitHub's default PostgreSQL credentials
    DATABASE_URL = "postgresql://postgres:asdqwe123@localhost:5432/test_db"
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    BaseORM.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    # Cleanup
    session.close()
    BaseORM.metadata.drop_all(engine)
    engine.dispose()