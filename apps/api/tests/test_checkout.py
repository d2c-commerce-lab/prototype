import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _signup_user(email: str) -> str:
    payload = {
        "email": email,
        "user_name": "checkout-test-user",
        "password": "Password123!",
        "marketing_opt_in_yn": True,
    }
    response = client.post("/auth/signup", json=payload)
    return response.json()["user_id"]


def _create_cart(user_id: str) -> str:
    response = client.post("/carts", json={"user_id": user_id})
    return response.json()["cart_id"]


def _add_item(cart_id: str, product_id: str, quantity: int = 1) -> None:
    client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": product_id, "quantity": quantity},
    )


def test_checkout_returns_200_for_valid_cart() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"checkout_user_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)

    response = client.post(f"/carts/{cart_id}/checkout")

    assert response.status_code == 200


def test_checkout_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"checkout_fields_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)

    response = client.post(f"/carts/{cart_id}/checkout")
    data = response.json()

    assert "cart_id" in data
    assert "user_id" in data
    assert "cart_status" in data
    assert "total_items" in data
    assert "total_quantity" in data
    assert "total_amount" in data
    assert "currency" in data
    assert "items" in data
    assert "user" in data
    assert "available_coupons" in data

    assert data["cart_id"] == cart_id
    assert data["user_id"] == user_id
    assert data["cart_status"] == "active"
    assert data["total_items"] == 1
    assert data["total_quantity"] == 2
    assert len(data["items"]) == 1


def test_checkout_returns_400_for_empty_cart() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"checkout_empty_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)

    response = client.post(f"/carts/{cart_id}/checkout")

    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"


def test_checkout_returns_404_for_missing_cart() -> None:
    response = client.post("/carts/99999999-9999-9999-9999-999999999999/checkout")

    assert response.status_code == 404
    assert response.json()["detail"] == "Active cart not found"