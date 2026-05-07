from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_product_detail_returns_200_for_existing_product() -> None:
    product_id = "33333333-3333-3333-3333-000000000001"

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200


def test_product_detail_returns_expected_fields() -> None:
    product_id = "33333333-3333-3333-3333-000000000001"

    response = client.get(f"/products/{product_id}")
    data = response.json()

    assert "product_id" in data
    assert "category_id" in data
    assert "product_name" in data
    assert "product_status" in data
    assert "list_price" in data
    assert "sale_price" in data
    assert "currency" in data
    assert "brand_name" in data
    assert "is_active" in data


def test_product_detail_returns_404_for_missing_product() -> None:
    product_id = "99999999-9999-9999-9999-999999999999"

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"