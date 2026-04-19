from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_health_endpoint_returns_200() -> None:
    response = client.get("/health")

    assert response.status_code == 200

def test_health_endpoint_returns_expected_keys() -> None:
    response = client.get("/health")
    data = response.json()
    
    assert "status" in data
    assert "database" in data
    assert data["status"] == "ok"