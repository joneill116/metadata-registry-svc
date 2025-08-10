from fastapi.testclient import TestClient
from src.metadata_registry_svc.main import app

def test_health_check():
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
