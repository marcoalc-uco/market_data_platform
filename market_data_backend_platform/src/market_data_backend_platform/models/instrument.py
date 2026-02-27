"""Instrument model for financial instruments.

This module defines the Instrument model representing stocks,
indices, and cryptocurrencies tracked by the platform.
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from market_data_backend_platform.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from market_data_backend_platform.models.market_price import MarketPrice


class InstrumentType(enum.Enum):
    """Types of financial instruments supported.

    Attributes:
        STOCK: Equity securities (e.g., AAPL, GOOGL).
        INDEX: Market indices (e.g., SPX, NDX).
        CRYPTO: Cryptocurrencies (e.g., BTC, ETH).
    """

    STOCK = "stock"
    INDEX = "index"
    CRYPTO = "crypto"


class Instrument(TimestampMixin, Base):
    """Model representing a financial instrument.

    An instrument is a tradeable asset like a stock, index, or cryptocurrency.
    Each instrument has a unique symbol used for identification.

    Attributes:
        id: Primary key.
        symbol: Unique ticker symbol (e.g., AAPL, BTC-USD).
        name: Full name of the instrument.
        instrument_type: Type of instrument (stock, index, crypto).
        exchange: Exchange where the instrument is traded.
        is_active: Whether the instrument is actively being tracked.
        prices: Relationship to associated MarketPrice records.
        created_at: Timestamp of record creation (from mixin).
        updated_at: Timestamp of last update (from mixin).
    """

    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    instrument_type: Mapped[InstrumentType] = mapped_column(
        Enum(InstrumentType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    exchange: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationship to MarketPrice records
    prices: Mapped[list["MarketPrice"]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of Instrument."""
        return (
            f"<Instrument(symbol='{self.symbol}', type={self.instrument_type.value})>"
        )
