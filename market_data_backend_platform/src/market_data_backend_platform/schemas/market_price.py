"""Pydantic schemas for MarketPrice.

This module defines request/response schemas for the MarketPrice API.
Schemas handle OHLCV data validation and serialization.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from market_data_backend_platform.schemas.instrument import InstrumentResponse


class MarketPriceBase(BaseModel):
    """Base schema with common MarketPrice fields.

    Attributes:
        timestamp: Date/time of the price data.
        open: Opening price.
        high: Highest price during the period.
        low: Lowest price during the period.
        close: Closing price.
        volume: Trading volume.
    """

    timestamp: datetime = Field(
        ...,
        description="Date/time of the price data (UTC)",
    )
    open: Decimal = Field(
        ...,
        ge=0,
        decimal_places=8,
        examples=["185.50"],
        description="Opening price",
    )
    high: Decimal = Field(
        ...,
        ge=0,
        decimal_places=8,
        examples=["186.20"],
        description="Highest price during the period",
    )
    low: Decimal = Field(
        ...,
        ge=0,
        decimal_places=8,
        examples=["185.00"],
        description="Lowest price during the period",
    )
    close: Decimal = Field(
        ...,
        ge=0,
        decimal_places=8,
        examples=["185.80"],
        description="Closing price",
    )
    volume: int = Field(
        ...,
        ge=0,
        examples=[1000000],
        description="Trading volume",
    )


class MarketPriceCreate(MarketPriceBase):
    """Schema for creating a new MarketPrice record.

    Attributes:
        instrument_id: ID of the associated instrument.
    """

    instrument_id: int = Field(
        ...,
        description="ID of the associated instrument",
    )


class MarketPriceResponse(MarketPriceBase):
    """Schema for MarketPrice API responses.

    Includes all base fields plus database-generated fields.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    instrument_id: int
    created_at: datetime
    updated_at: datetime


class MarketPriceWithInstrument(MarketPriceResponse):
    """MarketPrice response including nested Instrument data."""

    instrument: "InstrumentResponse"
