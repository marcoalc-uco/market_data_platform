"""Integration tests for the Health endpoint.

These tests validate the /health endpoint behavior.
"""

import pytest
from fastapi.testclient import TestClient

from market_data_backend_platform.main import app


# Fixture for test client
@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test cases for the /health endpoint.

    The health endpoint should:
    - Return HTTP 200 when service is healthy
    - Return JSON with status and version
    - Be accessible without authentication
    """

    def test_health_returns_200(self, client: TestClient) -> None:
        """Test that /health returns HTTP 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client: TestClient) -> None:
        """Test that /health returns JSON content type."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_contains_status(self, client: TestClient) -> None:
        """Test that response contains 'status' field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_contains_version(self, client: TestClient) -> None:
        """Test that response contains 'version' field."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)

    def test_health_response_structure(self, client: TestClient) -> None:
        """Test the complete response structure."""
        response = client.get("/health")
        data = response.json()

        # Should have exactly these fields
        assert set(data.keys()) == {"status", "version"}
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
