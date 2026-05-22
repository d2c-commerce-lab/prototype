from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_create_event_log_returns_201() -> None:
    response = client.post(
        "/events",
        json={
            "event_name": "product_detail_viewed",
            "event_type": "user_behavior",
            "source": "frontend",
            "user_id": None,
            "session_id": None,
            "entity_type": "product",
            "entity_id": "33333333-3333-3333-3333-000000000001",
            "properties": {
                "product_name": "Accessory Dock Pro",
                "source_page": "product_list",
            },
        },
    )

    assert response.status_code == 201


def test_create_event_log_returns_expected_fields() -> None:
    response = client.post(
        "/events",
        json={
            "event_name": "product_detail_viewed",
            "event_type": "user_behavior",
            "source": "frontend",
            "entity_type": "product",
            "entity_id": "33333333-3333-3333-3333-000000000001",
            "properties": {
                "product_name": "Accessory Dock Pro",
            },
        },
    )
    data = response.json()

    assert "event_id" in data
    assert data["event_name"] == "product_detail_viewed"
    assert data["event_type"] == "user_behavior"
    assert data["source"] == "frontend"
    assert data["entity_type"] == "product"
    assert data["entity_id"] == "33333333-3333-3333-3333-000000000001"
    assert "occurred_at" in data
    assert "created_at" in data
    assert data["message"] == "Event log recorded successfully"


def test_create_event_log_returns_400_for_unsupported_event_type() -> None:
    response = client.post(
        "/events",
        json={
            "event_name": "product_detail_viewed",
            "event_type": "invalid_type",
            "source": "frontend",
            "properties": {},
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported event type"


def test_create_event_log_returns_400_for_unsupported_source() -> None:
    response = client.post(
        "/events",
        json={
            "event_name": "product_detail_viewed",
            "event_type": "user_behavior",
            "source": "invalid_source",
            "properties": {},
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported event source"