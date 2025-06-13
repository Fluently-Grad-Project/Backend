from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api.user import router
from app.main import app

app.include_router(router)

# dummy user for testing
test_user_data = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@gmail.com",
    "password": "TestPass123",
    "gender": "male",
}


@pytest.fixture
def client():
    return TestClient(app)


# ---- Test 1: Successful registration ----
@patch("app.services.user_service.get_user_by_email", return_value=None)
@patch("app.services.user_service.create_user")
@patch("app.services.email_service.send_verification_email")
@patch("app.core.auth_manager.create_access_token", return_value="fake-access-token")
def test_register_success(
    mock_token, mock_email, mock_create_user, mock_get_user, client
):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.email = "test@gmail.com"
    mock_user.gender = "male"
    mock_user.is_verified = False
    mock_create_user.return_value = (mock_user, "abc123")

    response = client.post("/users/register", json=test_user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert "access_token" in response.json()
    assert "verification_link" in response.json()
    assert response.json()["user"]["email"] == test_user_data["email"]


# ---- Test 2: User already exists ----
@patch("app.services.user_service.get_user_by_email")
def test_register_existing_user(mock_get_user, client):
    mock_get_user.return_value = MagicMock()  # simulation for get user

    response = client.post("/users/register", json=test_user_data)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Email already exists"


# ---- Test 3: Internal server error ----
@patch("app.services.user_service.get_user_by_email", side_effect=Exception("DB Error"))
def test_register_internal_error(mock_get_user, client):
    response = client.post("/users/register", json=test_user_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An error occurred during registration" in response.json()["detail"]
