"""Tests for Instruments API endpoints.

This module contains TDD tests for the instruments CRUD API.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from market_data_backend_platform.main import app
from market_data_backend_platform.models import (
    Base,
    Instrument,
    InstrumentType,
    MarketPrice,
)


# Test database setup (SQLite in-memory)
@pytest.fixture(name="engine")
def fixture_engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(name="session")
def fixture_session(engine):
    """Create test database session."""
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(name="client")
def fixture_client(session: Session):
    """Create test client with overridden dependencies."""
    from market_data_backend_platform.api.dependencies import get_db_session
    from market_data_backend_platform.auth.dependencies import get_current_user

    def override_get_db_session():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = lambda: "test@market.com"
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestListInstruments:
    """Tests for GET /api/v1/instruments endpoint."""

    def test_list_instruments_empty(self, client: TestClient):
        """Should return empty list when no instruments exist."""
        response = client.get("/api/v1/instruments")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_instruments_returns_all(
        self,
        client: TestClient,
        session: Session,
    ):
        """Should return all instruments."""
        # Arrange: Create instruments
        instrument1 = Instrument(
            symbol="AAPL",
            name="Apple Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        instrument2 = Instrument(
            symbol="BTC",
            name="Bitcoin",
            instrument_type=InstrumentType.CRYPTO,
            exchange="BINANCE",
        )
        session.add_all([instrument1, instrument2])
        session.commit()

        # Act
        response = client.get("/api/v1/instruments")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        symbols = [item["symbol"] for item in data]
        assert "AAPL" in symbols
        assert "BTC" in symbols


class TestCreateInstrument:
    """Tests for POST /api/v1/instruments endpoint."""

    def test_create_instrument_success(self, client: TestClient):
        """Should create a new instrument."""
        payload = {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "instrument_type": "stock",
            "exchange": "NASDAQ",
        }

        response = client.post("/api/v1/instruments", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["symbol"] == "GOOGL"
        assert data["name"] == "Alphabet Inc."
        assert data["instrument_type"] == "stock"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_instrument_duplicate_symbol(
        self,
        client: TestClient,
        session: Session,
    ):
        """Should return 409 when symbol already exists."""
        # Arrange: Create existing instrument
        existing = Instrument(
            symbol="AAPL",
            name="Apple Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        session.add(existing)
        session.commit()

        # Act: Try to create duplicate
        payload = {
            "symbol": "AAPL",
            "name": "Apple (duplicate)",
            "instrument_type": "stock",
            "exchange": "NYSE",
        }
        response = client.post("/api/v1/instruments", json=payload)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT


class TestGetInstrument:
    """Tests for GET /api/v1/instruments/{id} endpoint."""

    def test_get_instrument_success(
        self,
        client: TestClient,
        session: Session,
    ):
        """Should return instrument by ID."""
        # Arrange
        instrument = Instrument(
            symbol="TSLA",
            name="Tesla Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        session.add(instrument)
        session.commit()
        session.refresh(instrument)

        # Act
        response = client.get(f"/api/v1/instruments/{instrument.id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["id"] == instrument.id

    def test_get_instrument_not_found(self, client: TestClient):
        """Should return 404 when instrument not found."""
        response = client.get("/api/v1/instruments/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateInstrument:
    """Tests for PATCH /api/v1/instruments/{id} endpoint."""

    def test_update_instrument_success(
        self,
        client: TestClient,
        session: Session,
    ):
        """Should update instrument fields."""
        # Arrange
        instrument = Instrument(
            symbol="MSFT",
            name="Microsoft",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        session.add(instrument)
        session.commit()
        session.refresh(instrument)

        # Act
        payload = {"name": "Microsoft Corporation", "is_active": False}
        response = client.patch(f"/api/v1/instruments/{instrument.id}", json=payload)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Microsoft Corporation"
        assert data["is_active"] is False
        assert data["symbol"] == "MSFT"  # Unchanged

    def test_update_instrument_not_found(self, client: TestClient):
        """Should return 404 when instrument not found."""
        response = client.patch("/api/v1/instruments/9999", json={"name": "Test"})

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteInstrument:
    """Tests for DELETE /api/v1/instruments/{id} endpoint."""

    def test_delete_instrument_success(
        self,
        client: TestClient,
        session: Session,
    ):
        """Should delete instrument."""
        # Arrange
        instrument = Instrument(
            symbol="AMZN",
            name="Amazon",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        session.add(instrument)
        session.commit()
        session.refresh(instrument)

        # Act
        response = client.delete(f"/api/v1/instruments/{instrument.id}")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(f"/api/v1/instruments/{instrument.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_instrument_not_found(self, client: TestClient):
        """Should return 404 when instrument not found."""
        response = client.delete("/api/v1/instruments/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetInstrumentPrices:
    """Tests for GET /api/v1/instruments/{id}/prices endpoint."""

    def test_get_prices_empty(
        self,
        client: TestClient,
        session: Session,
    ):
        """Should return empty list when no prices exist."""
        # Arrange
        instrument = Instrument(
            symbol="AAPL",
            name="Apple Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        session.add(instrument)
        session.commit()
        session.refresh(instrument)

        # Act
        response = client.get(f"/api/v1/instruments/{instrument.id}/prices")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_prices_returns_all(
        self,
        client: TestClient,
        session: Session,
    ):
        """Should return all prices for an instrument."""
        from datetime import datetime, timezone
        from decimal import Decimal

        # Arrange
        instrument = Instrument(
            symbol="AAPL",
            name="Apple Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        session.add(instrument)
        session.commit()
        session.refresh(instrument)

        price1 = MarketPrice(
            instrument_id=instrument.id,
            timestamp=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
            open=Decimal("185.00"),
            high=Decimal("186.00"),
            low=Decimal("184.00"),
            close=Decimal("185.50"),
            volume=1000000,
        )
        price2 = MarketPrice(
            instrument_id=instrument.id,
            timestamp=datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc),
            open=Decimal("185.50"),
            high=Decimal("187.00"),
            low=Decimal("185.00"),
            close=Decimal("186.00"),
            volume=1200000,
        )
        session.add_all([price1, price2])
        session.commit()

        # Act
        response = client.get(f"/api/v1/instruments/{instrument.id}/prices")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_prices_with_limit(
        self,
        client: TestClient,
        session: Session,
    ):
        """Should respect limit parameter."""
        from datetime import datetime, timezone
        from decimal import Decimal

        # Arrange
        instrument = Instrument(
            symbol="AAPL",
            name="Apple Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        session.add(instrument)
        session.commit()
        session.refresh(instrument)

        # Add 5 prices
        for i in range(5):
            price = MarketPrice(
                instrument_id=instrument.id,
                timestamp=datetime(2024, 1, 15, 10 + i, 0, tzinfo=timezone.utc),
                open=Decimal("185.00"),
                high=Decimal("186.00"),
                low=Decimal("184.00"),
                close=Decimal("185.50"),
                volume=1000000 + i,
            )
            session.add(price)
        session.commit()

        # Act
        response = client.get(f"/api/v1/instruments/{instrument.id}/prices?limit=3")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_get_prices_instrument_not_found(self, client: TestClient):
        """Should return 404 when instrument not found."""
        response = client.get("/api/v1/instruments/9999/prices")

        assert response.status_code == status.HTTP_404_NOT_FOUND
