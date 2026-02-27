"""Tests for SQLAlchemy model base classes and mixins.

These tests verify Base and TimestampMixin.
Tests use SQLite in-memory for independence from PostgreSQL.
"""

from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

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


class TestBaseModel:
    """Tests for the declarative Base class."""

    def test_base_is_declarative_base(self) -> None:
        """Test that Base is a valid SQLAlchemy DeclarativeBase."""
        from sqlalchemy.orm import DeclarativeBase

        from market_data_backend_platform.models import Base

        assert issubclass(Base, DeclarativeBase)

    def test_base_has_metadata(self) -> None:
        """Test that Base has metadata for table management."""
        from market_data_backend_platform.models import Base

        assert hasattr(Base, "metadata")
        assert Base.metadata is not None


class TestTimestampMixin:
    """Tests for the TimestampMixin."""

    def test_mixin_has_created_at_field(self) -> None:
        """Test that TimestampMixin defines created_at column."""
        from market_data_backend_platform.models import TimestampMixin

        assert hasattr(TimestampMixin, "created_at")

    def test_mixin_has_updated_at_field(self) -> None:
        """Test that TimestampMixin defines updated_at column."""
        from market_data_backend_platform.models import TimestampMixin

        assert hasattr(TimestampMixin, "updated_at")

    def test_created_at_defaults_to_current_time(self, test_engine: "Engine") -> None:
        """Test that created_at is automatically set on insert."""
        from market_data_backend_platform.models import Base, TimestampMixin

        class TestModel(TimestampMixin, Base):
            __tablename__ = "test_timestamp"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(50), default="test")

        Base.metadata.create_all(test_engine)
        session_factory = sessionmaker(bind=test_engine)
        session = session_factory()

        record = TestModel()
        session.add(record)
        session.commit()

        assert record.created_at is not None
        assert isinstance(record.created_at, datetime)

        session.close()
