from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_list_categories_returns_200() -> None:
    response = client.get("/categories")
    assert response.status_code == 200


def test_list_categories_returns_list() -> None:
    response = client.get("/categories")
    data = response.json()

    assert isinstance(data, list)


def test_list_categories_has_expected_fields() -> None:
    response = client.get("/categories")
    data = response.json()

    if not data:
        return
    
    first_item = data[0]

    assert "category_id" in first_item
    assert "category_name" in first_item
    assert "category_depth" in first_item
    assert "category_status" in first_item