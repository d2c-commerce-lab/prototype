import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _signup_user(email: str) -> str:
    payload = {
        "email": email,
        "user_name": "payment-test-user",
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


def test_simulate_payment_success_returns_200() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"payment_success_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)
    order_id = _create_order(cart_id)

    response = client.post(
        "/payments/simulate",
        json={
            "order_id": order_id,
            "payment_method": "card",
            "simulate_result": "success",
        },
    )

    assert response.status_code == 200


def test_simulate_payment_failed_returns_200() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"payment_failed_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)
    order_id = _create_order(cart_id)

    response = client.post(
        "/payments/simulate",
        json={
            "order_id": order_id,
            "payment_method": "card",
            "simulate_result": "failed",
        },
    )

    assert response.status_code == 200


def test_simulate_payment_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"payment_fields_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)
    _add_item(cart_id, "33333333-3333-3333-3333-000000000001", 2)
    order_id = _create_order(cart_id)

    response = client.post(
        "/payments/simulate",
        json={
            "order_id": order_id,
            "payment_method": "card",
            "simulate_result": "success",
        },
    )
    data = response.json()

    assert "payment_id" in data
    assert "order_id" in data
    assert "payment_method" in data
    assert "payment_status" in data
    assert "requested_amount" in data
    assert "approved_amount" in data
    assert "failed_reason" in data
    assert "paid_at" in data
    assert "created_at" in data
    assert "message" in data

    assert data["order_id"] == order_id
    assert data["payment_method"] == "card"
    assert data["payment_status"] == "paid"


def test_simulate_payment_returns_404_for_missing_order() -> None:
    response = client.post(
        "/payments/simulate",
        json={
            "order_id": "99999999-9999-9999-9999-999999999999",
            "payment_method": "card",
            "simulate_result": "success",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"