import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _create_test_user(email: str, password: str = "Password123!") -> None:
    payload = {
        "email": email,
        "user_name": "login-test-user",
        "password": password,
        "marketing_opt_in_yn": True,
    }
    client.post("/auth/signup", json=payload)


def test_login_returns_200_for_vaild_credentials() -> None:
    unique_suffix = str(int(time.time() * 1000))
    email = f"login_user_{unique_suffix}@example.com"
    password = "Password123!"

    _create_test_user(email=email, password=password)

    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200


def test_login_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    email = f"login_fields_{unique_suffix}@example.com"
    password = "Password123!"

    _create_test_user(email=email, password=password)

    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    data = response.json()

    assert "user_id" in data
    assert "email" in data
    assert "user_name" in data
    assert "user_status" in data
    assert "message" in data

    assert data["email"] == email
    assert data["user_status"] == "active"
    assert data["message"] == "Login successful"


def test_login_returns_401_for_invalid_email() -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "not-found@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_returns_401_for_invaild_password() -> None:
    unique_suffix = str(int(time.time() * 1000))
    email = f"login_invalid_pw_{unique_suffix}@example.com"

    _create_test_user(email=email, password="Password123!")

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"