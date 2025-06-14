import sys
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import get_db
from unittest.mock import patch

# Add project root to Python path (for imports)
sys.path.append(str(Path(__file__).parent.parent))

client = TestClient(app)

def test_successful_registration(db_session):
    """Test new user can register successfully"""
    # 1. Override database dependency
    app.dependency_overrides[get_db] = lambda: db_session
    print(f"ACTUAL DATABASE IN USE: {db_session.bind.url}")
    # 2. Prepare test data
    test_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test_user@example.com",  # Always unique
        "password": "Asdqwe123*",
        "gender": "FEMALE",
        "birth_date": "2000-01-01",
        "languages": ["English"],
        "proficiency_level": "INTERMEDIATE", 
        "practice_frequency": "15",
        "interests": ["Reading"]
    }
    
    # 3. Make request
    response = client.post("/users/register", json=test_data)
    
    # 4. Verify response
    assert response.status_code == 201, "Registration should succeed"
    assert "access_token" in response.json(), "Response should contain access token"
    
    # 5. Cleanup
    app.dependency_overrides.clear()

def test_duplicate_email(db_session):
    """Test duplicate email registration fails"""
    # 1. Override database dependency
    app.dependency_overrides[get_db] = lambda: db_session
    
    # 2. Prepare test data
    test_data = {
        "first_name": "Duplicate",
        "last_name": "User",
        "email": "duplicate@example.com",  # Same email for both attempts
        "password": "Asdqwe123*",
        "gender": "MALE",
        "birth_date": "1995-05-05",
        "languages": ["Spanish"],
        "proficiency_level": "BEGINNER",
        "practice_frequency": "10",
        "interests": ["Sports"]
    }
    
    # 3. First registration (should succeed)
    first_response = client.post("/users/register", json=test_data)
    assert first_response.status_code == 201, "First registration should work"
    
    # 4. Second registration (should fail)
    second_response = client.post("/users/register", json=test_data)
    
    # 5. Verify failure
    assert second_response.status_code == 409, "Should reject duplicate email"
    assert "already exists" in second_response.json()["detail"].lower()
    
    # 6. Cleanup
    app.dependency_overrides.clear()

'''input validation Tests'''
def test_register_invalid_email(db_session):
    """Test registration with invalid email format"""
    app.dependency_overrides[get_db] = lambda: db_session
    test_data = {
        "first_name": "Duplicate",
        "last_name": "User",
        "email": "not-an-email",  
        "password": "Asdqwe123*",
        "gender": "MALE",
        "birth_date": "1995-05-05",
        "languages": ["Spanish"],
        "proficiency_level": "BEGINNER",
        "practice_frequency": "10",
        "interests": ["Sports"]
    }
    
    response = client.post("/users/register", json=test_data)
    print("Response for invalid email format:")
    print(response.text)
    assert response.status_code == 422  
    assert "email" in response.text.lower()
def test_register_weak_password(db_session):
    """Test password complexity requirements"""
    app.dependency_overrides[get_db] = lambda: db_session
    test_data = {
        "first_name": "Duplicate",
        "last_name": "User",
        "email": "valid@example.com",  
        "password": "123",
        "gender": "MALE",
        "birth_date": "1995-05-05",
        "languages": ["Spanish"],
        "proficiency_level": "BEGINNER",
        "practice_frequency": "10",
        "interests": ["Sports"]
    }
    
    response = client.post("/users/register", json=test_data)
    assert response.status_code == 422
    assert "password" in response.text.lower()

    '''Test missing required fields"""'''
def test_register_missing_required_fields(db_session):
    """Test missing required fields"""
    app.dependency_overrides[get_db] = lambda: db_session
    test_data = {
        "first_name": "Duplicate",
        "last_name": "User",
        "email": "valid@example.com",  
        "password": "Asdqwe123*",
        
    }
    response = client.post("/users/register", json=test_data)
    assert response.status_code == 422
'''Error Handling Tests'''
def test_database_error_handling(db_session):
    """Test proper error handling when DB operations fail"""
    app.dependency_overrides[get_db] = lambda: db_session
    
    # Simulate DB failure
    with patch('sqlalchemy.orm.Session.commit', side_effect=Exception("DB error")):
        test_data = {
        "first_name": "Duplicate",
        "last_name": "User",
        "email": "duplicate@example.com",  
        "password": "Asdqwe123*",
        "gender": "MALE",
        "birth_date": "1995-05-05",
        "languages": ["Spanish"],
        "proficiency_level": "BEGINNER",
        "practice_frequency": "10",
        "interests": ["Sports"]
        }
        response = client.post("/users/register", json=test_data)
        print("Response for simulated DB error:")
        print(response.text)
        assert response.status_code == 500
        assert "error" in response.text.lower()
