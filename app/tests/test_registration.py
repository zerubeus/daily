from datetime import datetime, timedelta
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_httpx_post():
    with patch("app.services.smtp_client_service.httpx.post") as mock_post:
        yield mock_post


def test_register_user(client, redis_client):
    response = client.post(
        "/api/v1/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is False

    assert redis_client.keys()


def test_register_user_duplicate(client, redis_client):
    client.post(
        "/api/v1/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    response = client.post(
        "/api/v1/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Email already exists"


def test_activate_user_invalid_code(client, redis_client):
    response = client.post(
        "/api/v1/register",
        json={"email": "invalidcode@example.com", "password": "password123"},
    )
    user_id = response.json().get("id", None)
    assert user_id is not None, "User ID should not be None"

    redis_client.setex(f"activation_code:{user_id}", timedelta(minutes=1), b"5678")

    activation_response = client.post(
        "/api/v1/activate",
        json={"user_id": user_id, "code": "1234"},
        auth=("invalidcode@example.com", "password123"),
    )
    assert activation_response.status_code == 400
    assert activation_response.json() == {"detail": "Invalid or expired code"}


def test_activate_user_expired_code(client, redis_client):
    response = client.post(
        "/api/v1/register",
        json={"email": "expired@example.com", "password": "password123"},
    )
    user_id = response.json().get("id", None)
    assert user_id is not None, "User ID should not be None"

    redis_client.setex(f"activation_code:{user_id}", timedelta(minutes=1), b"1234")

    with patch("app.services.user_service.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(minutes=2)

        activation_response = client.post(
            "/api/v1/activate",
            json={"user_id": user_id, "code": "1234"},
            auth=("expired@example.com", "password123"),
        )
        assert activation_response.status_code == 400
        assert activation_response.json() == {"detail": "Invalid or expired code"}


if __name__ == "__main__":
    pytest.main()
