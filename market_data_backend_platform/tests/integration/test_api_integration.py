"""API integration tests.

Tests the containerized FastAPI application end-to-end.
Verifies API health, database connectivity, and CRUD operations.
"""

import uuid

import httpx
import pytest


class TestAPIHealth:
    """Test API health and availability."""

    def test_health_endpoint(self, api_client: httpx.Client) -> None:
        """Test that health endpoint returns 200."""
        response = api_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_openapi_docs_available(self, api_client: httpx.Client) -> None:
        """Test that OpenAPI documentation is accessible."""
        response = api_client.get("/docs")
        assert response.status_code == 200


class TestInstrumentsCRUD:
    """Test CRUD operations for instruments."""

    def test_list_instruments(self, api_client: httpx.Client) -> None:
        """Test listing all instruments."""
        response = api_client.get("/api/v1/instruments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_instrument(self, api_client: httpx.Client) -> None:
        """Test creating a new instrument."""
        unique_symbol = f"TEST_{uuid.uuid4().hex[:8].upper()}"
        instrument_data = {
            "symbol": unique_symbol,
            "name": "Test Instrument",
            "instrument_type": "stock",
            "exchange": "NASDAQ",
        }

        response = api_client.post("/api/v1/instruments", json=instrument_data)
        assert response.status_code == 201

        data = response.json()
        assert data["symbol"] == unique_symbol
        assert data["name"] == "Test Instrument"
        assert data["instrument_type"] == "stock"
        assert "id" in data

    def test_get_instrument_by_id(self, api_client: httpx.Client) -> None:
        """Test retrieving instrument by ID."""
        # First create an instrument
        unique_symbol = f"GET_{uuid.uuid4().hex[:8].upper()}"
        instrument_data = {
            "symbol": unique_symbol,
            "name": "Get Test Instrument",
            "instrument_type": "stock",
            "exchange": "NASDAQ",
        }
        create_response = api_client.post("/api/v1/instruments", json=instrument_data)
        instrument_id = create_response.json()["id"]

        # Then retrieve it by ID
        response = api_client.get(f"/api/v1/instruments/{instrument_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["symbol"] == unique_symbol
        assert data["id"] == instrument_id

    def test_get_nonexistent_instrument(self, api_client: httpx.Client) -> None:
        """Test retrieving non-existent instrument returns 404."""
        response = api_client.get("/api/v1/instruments/99999")
        assert response.status_code == 404


class TestMarketPrices:
    """Test market price endpoints."""

    def test_get_prices_for_instrument(self, api_client: httpx.Client) -> None:
        """Test retrieving prices for a specific instrument."""
        # First create an instrument
        unique_symbol = f"PRICE_{uuid.uuid4().hex[:8].upper()}"
        instrument_data = {
            "symbol": unique_symbol,
            "name": "Price Test Instrument",
            "instrument_type": "stock",
            "exchange": "NASDAQ",
        }
        inst_response = api_client.post("/api/v1/instruments", json=instrument_data)
        instrument_id = inst_response.json()["id"]

        # Test getting prices (should be empty initially)
        response = api_client.get(f"/api/v1/prices/{instrument_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_prices_nonexistent_instrument(self, api_client: httpx.Client) -> None:
        """Test retrieving prices for non-existent instrument returns 404."""
        response = api_client.get("/api/v1/prices/99999")
        assert response.status_code == 404

    def test_get_latest_price_no_data(self, api_client: httpx.Client) -> None:
        """Test getting latest price when no prices exist returns 404."""
        # First create an instrument
        unique_symbol = f"LATEST_{uuid.uuid4().hex[:8].upper()}"
        instrument_data = {
            "symbol": unique_symbol,
            "name": "Latest Test Instrument",
            "instrument_type": "stock",
            "exchange": "NASDAQ",
        }
        inst_response = api_client.post("/api/v1/instruments", json=instrument_data)
        instrument_id = inst_response.json()["id"]

        # Try to get latest price (should return 404 - no prices)
        response = api_client.get(f"/api/v1/prices/{instrument_id}/latest")
        assert response.status_code == 404
