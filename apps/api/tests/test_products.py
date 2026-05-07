from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_list_products_returns_200() -> None:
    response = client.get("/products")
    assert response.status_code == 200


def test_list_products_returns_list() -> None:
    response = client.get("/products")
    data = response.json()

    assert isinstance(data, list)


def test_list_products_has_expected_fields() -> None:
    response = client.get("/products")
    data = response.json()

    if not data:
        return
    
    first_item = data[0]

    assert "product_id" in first_item
    assert "category_id" in first_item
    assert "product_name" in first_item
    assert "product_status" in first_item
    assert "list_price" in first_item
    assert "sale_price" in first_item
    assert "currency" in first_item
    assert "brand_name" in first_item
    assert "is_active" in first_item