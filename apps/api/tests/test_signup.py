import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_signup_returns_201() -> None:
    unique_suffix = str(int(time.time() * 1000))
    payload = {
        "email": f"user_{unique_suffix}@example.com",
        "user_name": "test-user",
        "password": "Password123!",
        "marketing_opt_in_yn": True,
    }

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 201


def test_signup_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    payload = {
        "email": f"user_fields_{unique_suffix}@example.com",
        "user_name": "field-check-user",
        "password": "Password123!",
        "marketing_opt_in_yn": False,
    }

    response = client.post("/auth/signup", json=payload)
    data = response.json()

    assert "user_id" in data
    assert "email" in data
    assert "user_name" in data
    assert "user_status" in data
    assert "marketing_opt_in_yn" in data

    assert data["email"] == payload["email"]
    assert data["user_name"] == payload["user_name"]
    assert data["user_status"] == "active"
    assert data["marketing_opt_in_yn"] is False


def test_signup_returns_409_for_duplicate_email() -> None:
    unique_suffix = str(int(time.time() * 1000))
    payload = {
        "email": f"user_dup_{unique_suffix}@example.com",
        "user_name": "duplicate-user",
        "password": "Password123!",
        "marketing_opt_in_yn": True,
    }

    first_response = client.post("/auth/signup", json=payload)
    second_response = client.post("/auth/signup", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already exists"