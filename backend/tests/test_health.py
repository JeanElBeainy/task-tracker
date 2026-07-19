from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_shape():
    response = client.get("/health")
    data = response.json()

    assert set(data.keys()) == {"status", "timestamp"}
    assert data["status"] == "ok"


def test_health_check_timestamp_is_valid_iso_format():
    response = client.get("/health")
    data = response.json()

    # datetime.fromisoformat raises ValueError if the string isn't valid ISO 8601
    parsed = datetime.fromisoformat(data["timestamp"])
    assert parsed.tzinfo is not None
