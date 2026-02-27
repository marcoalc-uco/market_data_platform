"""Instruments API endpoints.

This module provides CRUD operations for financial instruments.
"""

from fastapi import APIRouter, HTTPException, status

from market_data_backend_platform.api.dependencies import (
    InstrumentRepoDep,
    MarketPriceRepoDep,
)
from market_data_backend_platform.schemas import (
    InstrumentCreate,
    InstrumentResponse,
    InstrumentUpdate,
    MarketPriceResponse,
)

router = APIRouter()


@router.get("", response_model=list[InstrumentResponse])
def list_instruments(repo: InstrumentRepoDep) -> list[InstrumentResponse]:
    """List all instruments.

    Args:
        repo: InstrumentRepository from dependency injection.

    Returns:
        List of all instruments.
    """
    instruments = repo.get_all()
    return [InstrumentResponse.model_validate(i) for i in instruments]


@router.post("", response_model=InstrumentResponse, status_code=status.HTTP_201_CREATED)
def create_instrument(
    payload: InstrumentCreate,
    repo: InstrumentRepoDep,
) -> InstrumentResponse:
    """Create a new instrument.

    Args:
        payload: Instrument data for creation.
        repo: InstrumentRepository from dependency injection.

    Returns:
        The created instrument.

    Raises:
        HTTPException: 409 if symbol already exists.
    """
    # Check for duplicate symbol
    existing = repo.get_by_symbol(payload.symbol)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Instrument with symbol '{payload.symbol}' already exists",
        )

    from market_data_backend_platform.models import Instrument

    instrument = Instrument(**payload.model_dump())
    created = repo.create(instrument)
    return InstrumentResponse.model_validate(created)


@router.get("/{instrument_id}", response_model=InstrumentResponse)
def get_instrument(
    instrument_id: int,
    repo: InstrumentRepoDep,
) -> InstrumentResponse:
    """Get instrument by ID.

    Args:
        instrument_id: ID of the instrument to retrieve.
        repo: InstrumentRepository from dependency injection.

    Returns:
        The instrument if found.

    Raises:
        HTTPException: 404 if instrument not found.
    """
    instrument = repo.get_by_id(instrument_id)
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument with id {instrument_id} not found",
        )
    return InstrumentResponse.model_validate(instrument)


@router.patch("/{instrument_id}", response_model=InstrumentResponse)
def update_instrument(
    instrument_id: int,
    payload: InstrumentUpdate,
    repo: InstrumentRepoDep,
) -> InstrumentResponse:
    """Update an instrument.

    Args:
        instrument_id: ID of the instrument to update.
        payload: Fields to update.
        repo: InstrumentRepository from dependency injection.

    Returns:
        The updated instrument.

    Raises:
        HTTPException: 404 if instrument not found.
    """
    instrument = repo.get_by_id(instrument_id)
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument with id {instrument_id} not found",
        )

    # Apply updates to the instrument object
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instrument, field, value)

    updated = repo.update(instrument)
    return InstrumentResponse.model_validate(updated)


@router.delete("/{instrument_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instrument(
    instrument_id: int,
    repo: InstrumentRepoDep,
) -> None:
    """Delete an instrument.

    Args:
        instrument_id: ID of the instrument to delete.
        repo: InstrumentRepository from dependency injection.

    Raises:
        HTTPException: 404 if instrument not found.
    """
    instrument = repo.get_by_id(instrument_id)
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument with id {instrument_id} not found",
        )

    repo.delete(instrument)


@router.get("/{instrument_id}/prices", response_model=list[MarketPriceResponse])
def get_instrument_prices(
    instrument_id: int,
    instrument_repo: InstrumentRepoDep,
    price_repo: MarketPriceRepoDep,
    limit: int | None = None,
) -> list[MarketPriceResponse]:
    """Get price history for an instrument.

    Args:
        instrument_id: ID of the instrument.
        instrument_repo: InstrumentRepository from dependency injection.
        price_repo: MarketPriceRepository from dependency injection.
        limit: Optional maximum number of prices to return.

    Returns:
        List of price records for the instrument.

    Raises:
        HTTPException: 404 if instrument not found.
    """
    # Verify instrument exists
    instrument = instrument_repo.get_by_id(instrument_id)
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument with id {instrument_id} not found",
        )

    prices = price_repo.get_by_instrument(instrument_id, limit=limit)
    return [MarketPriceResponse.model_validate(p) for p in prices]
