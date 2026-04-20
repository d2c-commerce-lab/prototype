import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _signup_user(email: str) -> str:
    payload = {
        "email": email,
        "user_name": "cart-test-user",
        "password": "Password123!",
        "marketing_opt_in_yn": True,
    }

    response = client.post("/auth/signup", json=payload)
    return response.json()["user_id"]


def test_create_cart_returns_201() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"cart_user_{unique_suffix}@example.com")

    response = client.post("/carts", json={"user_id": user_id})

    assert response.status_code == 201


def test_create_cart_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"cart_fields_{unique_suffix}@example.com")

    response = client.post("/carts", json={"user_id": user_id})
    data = response.json()

    assert "cart_id" in data
    assert "user_id" in data
    assert "cart_status" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "checked_out_at" in data

    assert data["user_id"] == user_id
    assert data["cart_status"] == "active"
    assert data["checked_out_at"] is None


def test_create_cart_returns_existing_active_cart_for_same_user() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"cart_existing_{unique_suffix}@example.com")

    first_response = client.post("/carts", json={"user_id": user_id})
    second_response = client.post("/carts", json={"user_id": user_id})

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_data["cart_id"] == second_data["cart_id"]