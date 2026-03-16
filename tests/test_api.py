from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns status."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"
    assert json_data["version"] == "1.0.0"

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"

def test_api_docs_available():
    """Test that API docs are accessible."""
    response = client.get("/api/docs")
    assert response.status_code == 200

def test_items_endpoint_structure():
    """Test GET /api/items endpoint returns correct structure."""
    response = client.get("/api/items?limit=10")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert "total" in json_data
    assert "success" in json_data
    assert isinstance(json_data["data"], list)

def test_filters_endpoint():
    """Test GET /api/filters endpoint."""
    response = client.get("/api/filters")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert "locations" in json_data["data"]
    assert "categories" in json_data["data"]
