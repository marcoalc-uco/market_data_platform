"""Tests for MarketPrice model.

Following TDD: These tests are written FIRST, before implementation.
Tests use SQLite in-memory for unit test independence.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


@pytest.fixture
def test_engine() -> "Engine":
    """Create a test engine with SQLite in-memory."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def test_session(test_engine: "Engine") -> Session:
    """Create a test session with tables created."""
    from market_data_backend_platform.models import Base

    Base.metadata.create_all(test_engine)
    session_factory = sessionmaker(bind=test_engine)
    session = session_factory()
    yield session
    session.close()


@pytest.fixture
def sample_instrument(test_session: Session) -> "Instrument":
    """Create a sample instrument for testing."""
    from market_data_backend_platform.models import Instrument, InstrumentType

    instrument = Instrument(
        symbol="AAPL",
        name="Apple Inc.",
        instrument_type=InstrumentType.STOCK,
        exchange="NASDAQ",
    )
    test_session.add(instrument)
    test_session.commit()
    return instrument


class TestMarketPriceModel:
    """Tests for the MarketPrice model."""

    def test_market_price_inherits_from_base(self) -> None:
        """Test that MarketPrice inherits from Base."""
        from market_data_backend_platform.models import Base, MarketPrice

        assert issubclass(MarketPrice, Base)

    def test_market_price_has_timestamp_mixin(self) -> None:
        """Test that MarketPrice has created_at and updated_at."""
        from market_data_backend_platform.models import MarketPrice

        assert hasattr(MarketPrice, "created_at")
        assert hasattr(MarketPrice, "updated_at")

    def test_market_price_table_name(self) -> None:
        """Test that MarketPrice has correct table name."""
        from market_data_backend_platform.models import MarketPrice

        assert MarketPrice.__tablename__ == "market_prices"

    def test_market_price_has_required_fields(self) -> None:
        """Test that MarketPrice has all required fields."""
        from market_data_backend_platform.models import MarketPrice

        required_fields = [
            "id",
            "instrument_id",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        for field in required_fields:
            assert hasattr(MarketPrice, field), f"Missing field: {field}"

    def test_create_market_price(
        self,
        test_engine: "Engine",
        test_session: Session,
        sample_instrument: "Instrument",
    ) -> None:
        """Test creating a MarketPrice record."""
        from market_data_backend_platform.models import MarketPrice

        price = MarketPrice(
            instrument_id=sample_instrument.id,
            timestamp=datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            open=Decimal("185.50"),
            high=Decimal("186.20"),
            low=Decimal("185.00"),
            close=Decimal("185.80"),
            volume=1000000,
        )
        test_session.add(price)
        test_session.commit()

        assert price.id is not None
        assert price.instrument_id == sample_instrument.id
        assert price.open == Decimal("185.50")
        assert price.close == Decimal("185.80")
        assert price.volume == 1000000

    def test_market_price_has_instrument_relationship(
        self,
        test_engine: "Engine",
        test_session: Session,
        sample_instrument: "Instrument",
    ) -> None:
        """Test that MarketPrice has relationship to Instrument."""
        from market_data_backend_platform.models import MarketPrice

        price = MarketPrice(
            instrument_id=sample_instrument.id,
            timestamp=datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            open=Decimal("100.00"),
            high=Decimal("101.00"),
            low=Decimal("99.00"),
            close=Decimal("100.50"),
            volume=500000,
        )
        test_session.add(price)
        test_session.commit()

        # Verify relationship works
        assert price.instrument is not None
        assert price.instrument.symbol == "AAPL"

    def test_market_price_unique_constraint(
        self,
        test_engine: "Engine",
        test_session: Session,
        sample_instrument: "Instrument",
    ) -> None:
        """Test that instrument_id + timestamp is unique."""
        from sqlalchemy.exc import IntegrityError

        from market_data_backend_platform.models import MarketPrice

        timestamp = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        price1 = MarketPrice(
            instrument_id=sample_instrument.id,
            timestamp=timestamp,
            open=Decimal("100.00"),
            high=Decimal("101.00"),
            low=Decimal("99.00"),
            close=Decimal("100.50"),
            volume=500000,
        )
        test_session.add(price1)
        test_session.commit()

        # Try to insert duplicate
        price2 = MarketPrice(
            instrument_id=sample_instrument.id,
            timestamp=timestamp,  # Same timestamp for same instrument
            open=Decimal("100.00"),
            high=Decimal("101.00"),
            low=Decimal("99.00"),
            close=Decimal("100.50"),
            volume=500000,
        )
        test_session.add(price2)

        with pytest.raises(IntegrityError):
            test_session.commit()
