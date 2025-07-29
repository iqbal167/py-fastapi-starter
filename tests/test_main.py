from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_main():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello World"
    assert "app_name" in data
    assert "version" in data
    assert "environment" in data


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "version" in data
    assert "environment" in data


def test_settings_endpoint():
    response = client.get("/settings")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "environment" in data
    assert "debug" in data
