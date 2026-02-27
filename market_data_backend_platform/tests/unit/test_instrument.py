"""Tests for Instrument model.

These tests verify the Instrument model and InstrumentType enum.
Tests use SQLite in-memory for unit test independence.
"""

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


class TestInstrumentModel:
    """Tests for the Instrument model."""

    def test_instrument_inherits_from_base(self) -> None:
        """Test that Instrument inherits from Base."""
        from market_data_backend_platform.models import Base, Instrument

        assert issubclass(Instrument, Base)

    def test_instrument_has_timestamp_mixin(self) -> None:
        """Test that Instrument has created_at and updated_at."""
        from market_data_backend_platform.models import Instrument

        assert hasattr(Instrument, "created_at")
        assert hasattr(Instrument, "updated_at")

    def test_instrument_table_name(self) -> None:
        """Test that Instrument has correct table name."""
        from market_data_backend_platform.models import Instrument

        assert Instrument.__tablename__ == "instruments"

    def test_instrument_has_required_fields(self) -> None:
        """Test that Instrument has all required fields."""
        from market_data_backend_platform.models import Instrument

        required_fields = ["id", "symbol", "name", "instrument_type", "exchange"]
        for field in required_fields:
            assert hasattr(Instrument, field), f"Missing field: {field}"

    def test_create_instrument(
        self, test_engine: "Engine", test_session: Session
    ) -> None:
        """Test creating an Instrument record."""
        from market_data_backend_platform.models import Instrument, InstrumentType

        instrument = Instrument(
            symbol="AAPL",
            name="Apple Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        test_session.add(instrument)
        test_session.commit()

        assert instrument.id is not None
        assert instrument.symbol == "AAPL"
        assert instrument.name == "Apple Inc."
        assert instrument.instrument_type == InstrumentType.STOCK
        assert instrument.is_active is True  # Default value

    def test_instrument_symbol_is_unique(
        self, test_engine: "Engine", test_session: Session
    ) -> None:
        """Test that symbol field enforces uniqueness."""
        from sqlalchemy.exc import IntegrityError

        from market_data_backend_platform.models import Instrument, InstrumentType

        instrument1 = Instrument(
            symbol="AAPL",
            name="Apple Inc.",
            instrument_type=InstrumentType.STOCK,
            exchange="NASDAQ",
        )
        test_session.add(instrument1)
        test_session.commit()

        instrument2 = Instrument(
            symbol="AAPL",  # Duplicate symbol
            name="Apple Corporation",
            instrument_type=InstrumentType.STOCK,
            exchange="NYSE",
        )
        test_session.add(instrument2)

        with pytest.raises(IntegrityError):
            test_session.commit()


class TestInstrumentType:
    """Tests for InstrumentType enum."""

    def test_instrument_type_values(self) -> None:
        """Test that InstrumentType has expected values."""
        from market_data_backend_platform.models import InstrumentType

        assert InstrumentType.STOCK.value == "stock"
        assert InstrumentType.INDEX.value == "index"
        assert InstrumentType.CRYPTO.value == "crypto"
