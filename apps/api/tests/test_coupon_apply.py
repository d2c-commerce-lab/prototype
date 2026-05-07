import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _signup_user(email: str) -> str:
    payload = {
        "email": email,
        "user_name": "coupon-test-user",
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


def test_apply_coupon_returns_200_for_valid_coupon() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"coupon_user_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)

    response = client.post(
        f"/carts/{cart_id}/coupon",
        json={"coupon_name": "WELCOME10"},
    )

    assert response.status_code == 200


def test_apply_coupon_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"coupon_fields_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)

    response = client.post(
        f"/carts/{cart_id}/coupon",
        json={"coupon_name": "WELCOME10"},
    )
    data = response.json()

    assert "cart_id" in data
    assert "coupon" in data
    assert "total_amount" in data
    assert "discount_amount" in data
    assert "final_amount" in data
    assert "currency" in data
    assert "message" in data

    assert data["cart_id"] == cart_id
    assert data["message"] == "Coupon applied successfully"


def test_apply_coupon_returns_404_for_missing_coupon() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"coupon_missing_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)

    response = client.post(
        f"/carts/{cart_id}/coupon",
        json={"coupon_name": "NOT_EXIST_COUPON"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Coupon not found"


def test_apply_coupon_returns_400_for_empty_cart() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"coupon_empty_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)

    response = client.post(
        f"/carts/{cart_id}/coupon",
        json={"coupon_name": "WELCOME10"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"