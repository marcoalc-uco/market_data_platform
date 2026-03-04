"""Pydantic schemas for Instrument.

This module defines request/response schemas for the Instrument API.
Schemas are separate from SQLAlchemy models to provide:
- Input validation
- Output serialization
- API documentation (OpenAPI)
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from market_data_backend_platform.models.instrument import InstrumentType


class InstrumentBase(BaseModel):
    """Base schema with common Instrument fields.

    ``instrument_type`` is exposed as ``asset_type`` in the API via a Pydantic
    alias so the JSON contract matches the frontend and the PRD.
    ``populate_by_name=True`` allows the Python attribute name to still be used
    internally (e.g. when constructing ORM objects from ``model_dump()``).

    Attributes:
        symbol: Unique ticker symbol (e.g., AAPL, BTC-USD).
        name: Full name of the instrument.
        instrument_type: Type of instrument – serialised/received as ``asset_type``.
        exchange: Exchange where the instrument is traded.
    """

    model_config = ConfigDict(populate_by_name=True)

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=20,
        examples=["AAPL", "BTC-USD"],
        description="Unique ticker symbol",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Apple Inc.", "Bitcoin USD"],
        description="Full name of the instrument",
    )
    instrument_type: InstrumentType = Field(
        ...,
        alias="asset_type",
        description="Type of financial instrument (stock | index | crypto)",
    )
    exchange: str = Field(
        ...,
        min_length=1,
        max_length=20,
        examples=["NASDAQ", "NYSE", "CRYPTO"],
        description="Exchange where the instrument is traded",
    )


class InstrumentCreate(InstrumentBase):
    """Schema for creating a new Instrument.

    Inherits all fields from InstrumentBase.
    Does not include id, is_active, or timestamps (set by DB).
    """


class InstrumentUpdate(BaseModel):
    """Schema for updating an existing Instrument.

    All fields are optional to allow partial updates.
    """

    name: str | None = Field(None, min_length=1, max_length=100)
    exchange: str | None = Field(None, min_length=1, max_length=20)
    is_active: bool | None = None


class InstrumentResponse(InstrumentBase):
    """Schema for Instrument API responses.

    Includes all base fields plus database-generated fields.

    Attributes:
        id: Primary key.
        is_active: Whether the instrument is actively tracked.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
