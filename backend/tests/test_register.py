from backend.app.core.security import verify_password
from backend.app.modules.auth.repository import get_user_by_email


def test_register_success(client, db_session):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["user"]["username"] == payload["username"]
    assert response.json()["user"]["email"] == payload["email"]

    user = get_user_by_email(db_session, payload["email"])

    assert user is not None
    assert user.password_hash != payload["password"]
    assert verify_password(payload["password"], user.password_hash)


def test_register_duplicate_email(client):
    payload = {
        "username": "user1",
        "email": "duplicate@example.com",
        "password": "password123",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)

    second_payload = {
        **payload,
        "username": "user2",
    }
    second_response = client.post(
        "/api/v1/auth/register",
        json=second_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_register_duplicate_username(client):
    payload = {
        "username": "duplicate",
        "email": "user1@example.com",
        "password": "password123",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)

    second_payload = {
        **payload,
        "email": "user2@example.com",
    }
    second_response = client.post(
        "/api/v1/auth/register",
        json=second_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_register_invalid_password(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123",
    }

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422
