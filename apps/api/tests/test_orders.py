import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _signup_user(email: str) -> str:
    payload = {
        "email": email,
        "user_name": "order-test-user",
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


def test_create_order_returns_201() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"order_user_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)

    response = client.post("/orders", json={"cart_id": cart_id})

    assert response.status_code == 201


def test_create_order_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"order_fields_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)

    response = client.post("/orders", json={"cart_id": cart_id})
    data = response.json()

    assert "order_id" in data
    assert "user_id" in data
    assert "cart_id" in data
    assert "order_status" in data
    assert "subtotal_amount" in data
    assert "discount_amount" in data
    assert "total_amount" in data
    assert "currency" in data
    assert "ordered_at" in data
    assert "items" in data
    assert "message" in data

    assert data["cart_id"] == cart_id
    assert data["user_id"] == user_id
    assert data["order_status"] == "created"
    assert data["message"] == "Order created successfully"
    assert len(data["items"]) == 1


def test_create_order_applies_coupon() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"order_coupon_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)

    response = client.post(
        "/orders",
        json={"cart_id": cart_id, "coupon_name": "WELCOME10"},
    )
    data = response.json()

    assert response.status_code == 201
    assert data["coupon_name"] == "WELCOME10"
    assert float(data["discount_amount"]) > 0
    assert float(data["final_amount" if "final_amount" in data else "total_amount"]) >= 0


def test_create_order_returns_400_for_empty_cart() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"order_empty_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)

    response = client.post("/orders", json={"cart_id": cart_id})

    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"


def test_create_order_returns_404_for_missing_cart() -> None:
    response = client.post(
        "/orders",
        json={"cart_id": "99999999-9999-9999-9999-999999999999"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Active cart not found"