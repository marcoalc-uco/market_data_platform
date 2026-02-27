"""Tests for Repository Pattern implementation.

Tests use SQLite in-memory for unit test independence.
"""

from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


@pytest.fixture
def test_engine() -> "Generator[Engine, None, None]":
    """Create a test engine with SQLite in-memory, disposed after the test."""
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()


@pytest.fixture
def test_session(test_engine: "Engine") -> Session:
    """Create a test session with tables created."""
    from market_data_backend_platform.models import Base

    Base.metadata.create_all(test_engine)
    session_factory = sessionmaker(bind=test_engine)
    session = session_factory()
    yield session
    session.close()


class TestBaseRepository:
    """Tests for the generic BaseRepository."""

    def test_base_repository_create(self, test_session: Session) -> None:
        """Test creating a record through repository."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        instrument = Instrument(
            symbol="AAPL",
            name="Apple Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )

        created = repo.create(instrument)

        assert created.id is not None
        assert created.symbol == "AAPL"

    def test_base_repository_get_by_id(self, test_session: Session) -> None:
        """Test getting a record by ID."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        instrument = Instrument(
            symbol="GOOGL",
            name="Alphabet Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        created = repo.create(instrument)

        found = repo.get_by_id(created.id)

        assert found is not None
        assert found.symbol == "GOOGL"

    def test_base_repository_get_by_id_not_found(self, test_session: Session) -> None:
        """Test getting a non-existent record returns None."""
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)

        found = repo.get_by_id(999)

        assert found is None

    def test_base_repository_get_all(self, test_session: Session) -> None:
        """Test getting all records."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        repo.create(
            Instrument(
                symbol="AAPL",
                name="Apple",
                instrument_type=InstrumentType.STOCK,
                exchange="NASDAQ",
            )
        )
        repo.create(
            Instrument(
                symbol="GOOGL",
                name="Alphabet",
                instrument_type=InstrumentType.STOCK,
                exchange="NASDAQ",
            )
        )

        all_instruments = repo.get_all()

        assert len(all_instruments) == 2

    def test_base_repository_update(self, test_session: Session) -> None:
        """Test updating a record."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        instrument = repo.create(
            Instrument(
                symbol="AAPL",
                name="Apple",
                instrument_type=InstrumentType.STOCK,
                exchange="NASDAQ",
            )
        )

        instrument.name = "Apple Inc."
        updated = repo.update(instrument)

        assert updated.name == "Apple Inc."

    def test_base_repository_delete(self, test_session: Session) -> None:
        """Test deleting a record."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        instrument = repo.create(
            Instrument(
                symbol="AAPL",
                name="Apple",
                instrument_type=InstrumentType.STOCK,
                exchange="NASDAQ",
            )
        )
        instrument_id = instrument.id

        repo.delete(instrument)

        assert repo.get_by_id(instrument_id) is None


class TestInstrumentRepository:
    """Tests for InstrumentRepository-specific methods."""

    def test_get_by_symbol(self, test_session: Session) -> None:
        """Test getting an instrument by symbol."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        repo.create(
            Instrument(
                symbol="BTC-USD",
                name="Bitcoin",
                instrument_type=InstrumentType.CRYPTO,
                exchange="CRYPTO",
            )
        )

        found = repo.get_by_symbol("BTC-USD")

        assert found is not None
        assert found.name == "Bitcoin"

    def test_get_by_symbol_not_found(self, test_session: Session) -> None:
        """Test getting non-existent symbol returns None."""
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)

        found = repo.get_by_symbol("NONEXISTENT")

        assert found is None

    def test_get_active_instruments(self, test_session: Session) -> None:
        """Test getting only active instruments."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        repo.create(
            Instrument(
                symbol="AAPL",
                name="Apple",
                instrument_type=InstrumentType.STOCK,
                exchange="NASDAQ",
                is_active=True,
            )
        )
        repo.create(
            Instrument(
                symbol="DEAD",
                name="Defunct Company",
                instrument_type=InstrumentType.STOCK,
                exchange="NYSE",
                is_active=False,
            )
        )

        active = repo.get_active()

        assert len(active) == 1
        assert active[0].symbol == "AAPL"

    def test_get_by_type(self, test_session: Session) -> None:
        """Test getting instruments by type."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        repo.create(
            Instrument(
                symbol="AAPL",
                name="Apple",
                instrument_type=InstrumentType.STOCK,
                exchange="NASDAQ",
            )
        )
        repo.create(
            Instrument(
                symbol="BTC-USD",
                name="Bitcoin",
                instrument_type=InstrumentType.CRYPTO,
                exchange="CRYPTO",
            )
        )

        stocks = repo.get_by_type(InstrumentType.STOCK)

        assert len(stocks) == 1
        assert stocks[0].symbol == "AAPL"


class TestMarketPriceRepository:
    """Tests for MarketPriceRepository-specific methods."""

    @pytest.fixture
    def sample_instrument(self, test_session: Session) -> "Instrument":
        """Create a sample instrument for price tests."""
        from market_data_backend_platform.models import Instrument, InstrumentType
        from market_data_backend_platform.repositories import InstrumentRepository

        repo = InstrumentRepository(test_session)
        return repo.create(
            Instrument(
                symbol="AAPL",
                name="Apple Inc.",
                instrument_type=InstrumentType.STOCK,
                exchange="NASDAQ",
            )
        )

    def test_get_existing_timestamps(
        self, test_session: Session, sample_instrument: "Instrument"
    ) -> None:
        """Test getting existing timestamps for an instrument.

        This is key for idempotent insertion.
        """
        from datetime import datetime, timezone

        from market_data_backend_platform.models import MarketPrice
        from market_data_backend_platform.repositories import MarketPriceRepository

        repo = MarketPriceRepository(test_session)

        # Create some existing prices (use naive datetimes for SQLite compatibility)
        ts1 = datetime(2024, 1, 15)
        ts2 = datetime(2024, 1, 16)

        repo.bulk_create(
            [
                MarketPrice(
                    instrument_id=sample_instrument.id,
                    timestamp=ts1,
                    open=185.00,
                    high=186.00,
                    low=184.00,
                    close=185.50,
                    volume=1000000,
                ),
                MarketPrice(
                    instrument_id=sample_instrument.id,
                    timestamp=ts2,
                    open=186.00,
                    high=187.00,
                    low=185.00,
                    close=186.50,
                    volume=1100000,
                ),
            ]
        )

        # Act: Get existing timestamps
        existing = repo.get_existing_timestamps(
            instrument_id=sample_instrument.id,
            timestamps=[ts1, ts2, datetime(2024, 1, 17)],
        )

        # Assert: Only ts1 and ts2 should be returned
        assert len(existing) == 2
        assert ts1 in existing
        assert ts2 in existing

    def test_bulk_create_new_filters_duplicates(
        self, test_session: Session, sample_instrument: "Instrument"
    ) -> None:
        """Test that bulk_create_new only inserts non-existing prices.

        This ensures idempotent behavior.
        """
        from datetime import datetime

        from market_data_backend_platform.models import MarketPrice
        from market_data_backend_platform.repositories import MarketPriceRepository

        repo = MarketPriceRepository(test_session)

        # Pre-existing price (use naive datetime for SQLite)
        ts_existing = datetime(2024, 1, 15)
        repo.bulk_create(
            [
                MarketPrice(
                    instrument_id=sample_instrument.id,
                    timestamp=ts_existing,
                    open=185.00,
                    high=186.00,
                    low=184.00,
                    close=185.50,
                    volume=1000000,
                ),
            ]
        )

        # New prices to insert (one duplicate, one new)
        ts_new = datetime(2024, 1, 16)
        new_prices = [
            MarketPrice(
                instrument_id=sample_instrument.id,
                timestamp=ts_existing,  # Duplicate!
                open=999.00,
                high=999.00,
                low=999.00,
                close=999.00,
                volume=999,
            ),
            MarketPrice(
                instrument_id=sample_instrument.id,
                timestamp=ts_new,  # New
                open=186.00,
                high=187.00,
                low=185.00,
                close=186.50,
                volume=1100000,
            ),
        ]

        # Act: Insert with idempotent method
        inserted = repo.bulk_create_new(new_prices)

        # Assert: Only the new price was inserted
        assert len(inserted) == 1
        assert inserted[0].timestamp == ts_new

        # Verify total count in DB
        all_prices = repo.get_by_instrument(sample_instrument.id)
        assert len(all_prices) == 2  # Original + 1 new (not 3!)
