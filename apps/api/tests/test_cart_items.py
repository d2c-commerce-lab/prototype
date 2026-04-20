import time

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _signup_user(email: str) -> str:
    payload = {
        "email": email,
        "user_name": "cart-item-test-user",
        "password": "Password123!",
        "marketing_opt_in_yn": True,
    }
    response = client.post("/auth/signup", json=payload)
    return response.json()["user_id"]


def _create_cart(user_id: str) -> str:
    response = client.post("/carts", json={"user_id": user_id})
    return response.json()["cart_id"]


def test_add_item_to_cart_returns_201() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"cart_item_user_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)

    payload = {
        "product_id": "33333333-3333-3333-3333-000000000001",
        "quantity": 1,
    }

    response = client.post(f"/carts/{cart_id}/items", json=payload)

    assert response.status_code == 201


def test_add_item_to_cart_returns_expected_fields() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"cart_item_fields_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)

    payload = {
        "product_id": "33333333-3333-3333-3333-000000000001",
        "quantity": 2,
    }

    response = client.post(f"/carts/{cart_id}/items", json=payload)
    data = response.json()

    assert "cart_item_id" in data
    assert "cart_id" in data
    assert "product_id" in data
    assert "quantity" in data
    assert "unit_price" in data
    assert "currency" in data
    assert "added_at" in data
    assert "updated_at" in data

    assert data["cart_id"] == cart_id
    assert data["product_id"] == payload["product_id"]
    assert data["quantity"] == 2


def test_add_item_to_cart_increases_quantity_for_existing_product() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"cart_item_existing_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)

    payload = {
        "product_id": "33333333-3333-3333-3333-000000000001",
        "quantity": 1,
    }

    first_response = client.post(f"/carts/{cart_id}/items", json=payload)
    second_response = client.post(f"/carts/{cart_id}/items", json=payload)

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_data["cart_item_id"] == second_data["cart_item_id"]
    assert second_data["quantity"] == 2


def test_add_item_to_cart_returns_404_for_missing_cart() -> None:
    payload = {
        "product_id": "33333333-3333-3333-3333-000000000001",
        "quantity": 1,
    }

    response = client.post(
        "/carts/99999999-9999-9999-9999-999999999999/items",
        json=payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Active cart not found"


def test_add_item_to_cart_returns_404_for_missing_product() -> None:
    unique_suffix = str(int(time.time() * 1000))
    user_id = _signup_user(f"cart_item_missing_{unique_suffix}@example.com")
    cart_id = _create_cart(user_id)

    payload = {
        "product_id": "99999999-9999-9999-9999-999999999999",
        "quantity": 1,
    }

    response = client.post(f"/carts/{cart_id}/items", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"