from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    # /health не трогает БД, поэтому этот тест работает без поднятого Postgres —
    # его можно гонять даже без docker compose, прямо из IDE.
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
