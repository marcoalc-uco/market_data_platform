"""MarketPrice model for historical price data.

This module defines the MarketPrice model representing OHLCV
(Open, High, Low, Close, Volume) data points for financial instruments.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from market_data_backend_platform.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from market_data_backend_platform.models.instrument import Instrument


class MarketPrice(TimestampMixin, Base):
    """Model representing a historical price data point.

    Each record stores OHLCV data for a specific instrument at a specific
    timestamp. The combination of instrument_id and timestamp must be unique.

    Attributes:
        id: Primary key.
        instrument_id: Foreign key to the Instrument.
        timestamp: Date/time of the price data.
        open: Opening price.
        high: Highest price during the period.
        low: Lowest price during the period.
        close: Closing price.
        volume: Trading volume.
        instrument: Relationship to the parent Instrument.
        created_at: Timestamp of record creation (from mixin).
        updated_at: Timestamp of last update (from mixin).

    Example::

        from market_data_backend_platform.models import MarketPrice, Instrument
        from datetime import datetime, timezone
        from decimal import Decimal

        price = MarketPrice(
            instrument_id=1,
            timestamp=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
            open=Decimal("185.50"),
            high=Decimal("186.20"),
            low=Decimal("185.00"),
            close=Decimal("185.80"),
            volume=1000000,
        )
    """

    __tablename__ = "market_prices"

    # Unique constraint: one price per instrument per timestamp
    __table_args__ = (
        UniqueConstraint("instrument_id", "timestamp", name="uq_instrument_timestamp"),
        Index("ix_market_prices_instrument_timestamp", "instrument_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # OHLCV data - using Numeric for precise decimal handling
    open: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8),
        nullable=False,
    )

    high: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8),
        nullable=False,
    )

    low: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8),
        nullable=False,
    )

    close: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8),
        nullable=False,
    )

    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # Relationship to Instrument
    instrument: Mapped["Instrument"] = relationship(
        back_populates="prices",
    )

    def __repr__(self) -> str:
        """Return string representation of MarketPrice."""
        return (
            f"<MarketPrice(instrument_id={self.instrument_id}, "
            f"timestamp={self.timestamp}, close={self.close})>"
        )
