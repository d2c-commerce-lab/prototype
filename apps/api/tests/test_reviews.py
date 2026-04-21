import time

from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.db.connection import engine
from backend.main import app

client = TestClient(app)


def _signup_user(email: str) -> str:
    payload = {
        "email": email,
        "user_name": "review-test-user",
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


def _pay_order(order_id: str) -> None:
    client.post(
        "/payments/simulate",
        json={
            "order_id": order_id,
            "payment_method": "card",
            "simulate_result": "success",
        },
    )


def _get_order_item_id(order_id: str, product_id: str) -> str:
    query = text("""
        SELECT
            order_item_id
        FROM order_items
        WHERE order_id = :order_id
          AND product_id = :product_id
        LIMIT 1
    """)

    with engine.connect() as connection:
        row = connection.execute(
            query,
            {
                "order_id": order_id,
                "product_id": product_id,
            },
        ).mappings().first()

    assert row is not None
    return str(row["order_item_id"])


def test_create_review_returns_201() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"review_user_{unique_suffix}@example.com")
    product_id = "33333333-3333-3333-3333-000000000001"

    cart_id = _create_cart(user_id)
    _add_item(cart_id, product_id, 1)
    order_id = _create_order(cart_id)
    _pay_order(order_id)
    order_item_id = _get_order_item_id(order_id, product_id)

    response = client.post(
        "/reviews",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "order_item_id": order_item_id,
            "rating": 5,
            "review_title": "Great product",
            "review_content": "The product quality is excellent.",
        },
    )

    assert response.status_code == 201


def test_create_review_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"review_fields_{unique_suffix}@example.com")
    product_id = "33333333-3333-3333-3333-000000000001"

    cart_id = _create_cart(user_id)
    _add_item(cart_id, product_id, 1)
    order_id = _create_order(cart_id)
    _pay_order(order_id)
    order_item_id = _get_order_item_id(order_id, product_id)

    response = client.post(
        "/reviews",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "order_item_id": order_item_id,
            "rating": 4,
            "review_title": "Solid item",
            "review_content": "Useful for daily desk setup.",
        },
    )
    data = response.json()

    assert "review_id" in data
    assert "user_id" in data
    assert "product_id" in data
    assert "order_item_id" in data
    assert "rating" in data
    assert "review_title" in data
    assert "review_content" in data
    assert "review_status" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "message" in data

    assert data["user_id"] == user_id
    assert data["product_id"] == product_id
    assert data["order_item_id"] == order_item_id
    assert data["rating"] == 4
    assert data["review_title"] == "Solid item"
    assert data["message"] == "Review created successfully"


def test_create_review_returns_400_for_non_purchased_product() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"review_not_purchased_{unique_suffix}@example.com")

    response = client.post(
        "/reviews",
        json={
            "user_id": user_id,
            "product_id": "33333333-3333-3333-3333-000000000001",
            "order_item_id": "99999999-9999-9999-9999-999999999999",
            "rating": 3,
            "review_title": "Cannot review",
            "review_content": "I did not buy this product.",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Review can only be created for purchased products"


def test_create_review_returns_409_for_duplicate_review() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"review_duplicate_{unique_suffix}@example.com")
    product_id = "33333333-3333-3333-3333-000000000001"

    cart_id = _create_cart(user_id)
    _add_item(cart_id, product_id, 1)
    order_id = _create_order(cart_id)
    _pay_order(order_id)
    order_item_id = _get_order_item_id(order_id, product_id)

    payload = {
        "user_id": user_id,
        "product_id": product_id,
        "order_item_id": order_item_id,
        "rating": 5,
        "review_title": "Great product",
        "review_content": "The product quality is excellent.",
    }

    first_response = client.post("/reviews", json=payload)
    second_response = client.post("/reviews", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Review already exists for this order item"