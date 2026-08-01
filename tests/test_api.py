import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data

def test_api_v1_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "database" in data
    assert "storage" in data

def test_unauthenticated_protected_route():
    response = client.get("/api/v1/resume/active")
    assert response.status_code == 401
