from fastapi.testclient import TestClient

from app.main import app


def test_health_responds_without_db():
    # The endpoint must answer even when Postgres is down; db=False in that case.
    with TestClient(app) as client:
        resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert isinstance(body["db"], bool)
