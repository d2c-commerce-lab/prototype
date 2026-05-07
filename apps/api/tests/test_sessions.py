from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_start_session_returns_201() -> None:
    payload = {
        "anonymous_id": "anon-session-001",
        "platform": "web",
        "device_type": "desktop",
        "os_type": "windows",
        "browser_type": "chrome",
        "traffic_source": "google",
        "traffic_medium": "organic",
        "landing_page_url": "/",
        "referrer_url": "https://www.google.com",
    }

    response = client.post("/sessions/start", json=payload)

    assert response.status_code == 201


def test_start_session_returns_expected_fields() -> None:
    payload = {
        "anonymous_id": "anon-session-002",
        "platform": "web",
        "device_type": "desktop",
        "os_type": "windows",
        "browser_type": "chrome",
        "traffic_source": "direct",
        "traffic_medium": "none",
        "landing_page_url": "/products",
        "referrer_url": None,
    }

    response = client.post("/sessions/start", json=payload)
    data = response.json()

    assert "session_id" in data
    assert "anonymous_id" in data
    assert "session_start_at" in data
    assert "session_end_at" in data
    assert "platform" in data
    assert "device_type" in data

    assert data["anonymous_id"] == payload["anonymous_id"]
    assert data["platform"] == payload["platform"]
    assert data["device_type"] == payload["device_type"]
    assert data["session_end_at"] is None


def test_end_session_returns_200() -> None:
    start_payload = {
        "anonymous_id": "anon-session-003",
        "platform": "web",
        "device_type": "mobile",
        "os_type": "android",
        "browser_type": "chrome",
        "traffic_source": "instagram",
        "traffic_medium": "social",
        "landing_page_url": "/categories",
        "referrer_url": "https://instagram.com",
    }

    start_response = client.post("/sessions/start", json=start_payload)
    session_id = start_response.json()["session_id"]

    end_response = client.patch(f"/sessions/{session_id}/end")

    assert end_response.status_code == 200


def test_end_session_returns_404_for_missing_session() -> None:
    response = client.patch("/sessions/99999999-9999-9999-9999-999999999999/end")

    assert response.status_code == 404
    assert response.json()["detail"] == "Active session not found"