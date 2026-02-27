"""Unit tests for auth routes.

TDD: these tests are written before the implementation.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from market_data_backend_platform.api.dependencies import (
    get_instrument_repository,
    get_market_price_repository,
)
from market_data_backend_platform.core.config import settings as _settings
from market_data_backend_platform.main import app

# Bcrypt hash of "adminpassword" — fixed value so tests are environment-independent.
# Never load auth credentials from .env in unit tests.
_TEST_ADMIN_HASH = "$2b$12$B9NxCdpM3Tz3YnxkXTqaw.trJaR.lz0bz9uzK5X56Au2FVuV23aLG"
_TEST_ADMIN_EMAIL = "admin@market.com"


@pytest.fixture
def client() -> TestClient:
    """Test client with mocked DB repositories and isolated auth settings.

    Patches admin_password_hash and admin_email on the settings singleton so
    that tests are independent of any local .env file.
    """
    mock_instrument_repo = MagicMock()
    mock_instrument_repo.get_all.return_value = []
    mock_price_repo = MagicMock()

    app.dependency_overrides[get_instrument_repository] = lambda: mock_instrument_repo
    app.dependency_overrides[get_market_price_repository] = lambda: mock_price_repo

    with (
        patch.object(_settings, "admin_password_hash", _TEST_ADMIN_HASH),
        patch.object(_settings, "admin_email", _TEST_ADMIN_EMAIL),
    ):
        yield TestClient(app)

    app.dependency_overrides.clear()


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/token."""

    def test_login_with_valid_credentials_returns_200(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin@market.com", "password": "adminpassword"},
        )
        assert response.status_code == 200

    def test_login_returns_access_token(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin@market.com", "password": "adminpassword"},
        )
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_with_wrong_password_returns_401(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin@market.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_with_unknown_user_returns_401(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "unknown@market.com", "password": "password"},
        )
        assert response.status_code == 401

    def test_login_with_missing_fields_returns_422(self, client: TestClient) -> None:
        response = client.post("/api/v1/auth/token", data={})
        assert response.status_code == 422


class TestProtectedRoutes:
    """Tests for routes requiring authentication."""

    def test_instruments_without_token_returns_401(self, client: TestClient) -> None:
        response = client.get("/api/v1/instruments")
        assert response.status_code == 401

    def test_prices_without_token_returns_401(self, client: TestClient) -> None:
        response = client.get("/api/v1/prices/1")
        assert response.status_code == 401

    def test_instruments_with_valid_token_returns_200(self, client: TestClient) -> None:
        login = client.post(
            "/api/v1/auth/token",
            data={"username": "admin@market.com", "password": "adminpassword"},
        )
        token = login.json()["access_token"]
        response = client.get(
            "/api/v1/instruments",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_instruments_with_invalid_token_returns_401(
        self, client: TestClient
    ) -> None:
        response = client.get(
            "/api/v1/instruments",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_health_without_token_returns_200(self, client: TestClient) -> None:
        """Health endpoint must remain public."""
        response = client.get("/health")
        assert response.status_code == 200
