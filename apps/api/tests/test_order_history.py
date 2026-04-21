import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _signup_user(email: str) -> str:
    payload = {
        "email": email,
        "user_name": "order-history-test-user",
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


def _create_order(cart_id: str) -> str:
    response = client.post("/orders", json={"cart_id": cart_id})
    return response.json()["order_id"]


def test_get_order_history_returns_200() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"order_history_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)
    _create_order(cart_id)

    response = client.get(f"/orders?user_id={user_id}")

    assert response.status_code == 200


def test_get_order_history_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"order_history_fields_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)
    _create_order(cart_id)

    response = client.get(f"/orders?user_id={user_id}")
    data = response.json()

    assert "user_id" in data
    assert "total_orders" in data
    assert "orders" in data

    assert data["user_id"] == user_id
    assert data["total_orders"] == 1
    assert isinstance(data["orders"], list)
    assert len(data["orders"]) == 1

    order = data["orders"][0]
    assert "order_id" in order
    assert "order_status" in order
    assert "payment_status" in order
    assert "subtotal_amount" in order
    assert "discount_amount" in order
    assert "total_amount" in order
    assert "currency" in order
    assert "ordered_at" in order
    assert "items" in order

    assert isinstance(order["items"], list)
    assert len(order["items"]) == 1


def test_get_order_history_returns_empty_list_for_no_orders() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"order_history_empty_{unique_suffix}@example.com")

    response = client.get(f"/orders?user_id={user_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["user_id"] == user_id
    assert data["total_orders"] == 0
    assert data["orders"] == []


def test_get_order_history_returns_404_for_missing_user() -> None:
    response = client.get("/orders?user_id=99999999-9999-9999-9999-999999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"