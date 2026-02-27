"""Prices API endpoints.

This module provides query endpoints for market price data
with filtering, pagination, and date range support.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from market_data_backend_platform.api.dependencies import (
    InstrumentRepoDep,
    MarketPriceRepoDep,
)
from market_data_backend_platform.schemas import MarketPriceResponse

router = APIRouter()


@router.get(
    "/{instrument_id}",
    response_model=list[MarketPriceResponse],
    summary="Get prices by instrument",
)
def get_prices(
    instrument_id: int,
    instrument_repo: InstrumentRepoDep,
    price_repo: MarketPriceRepoDep,
    start_date: datetime | None = Query(
        None,
        description="Filter prices from this date (inclusive)",
    ),
    end_date: datetime | None = Query(
        None,
        description="Filter prices until this date (inclusive)",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of prices to return",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of prices to skip (for pagination)",
    ),
) -> list[MarketPriceResponse]:
    """Get price history for an instrument with optional filtering.

    Args:
        instrument_id: ID of the instrument.
        instrument_repo: Injected InstrumentRepository.
        price_repo: Injected MarketPriceRepository.
        start_date: Optional start of date range filter.
        end_date: Optional end of date range filter.
        limit: Max records to return (default 100, max 1000).
        offset: Records to skip for pagination.

    Returns:
        List of market prices matching the criteria.

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

    # Query based on filters
    if start_date and end_date:
        prices = price_repo.get_by_date_range(
            instrument_id=instrument_id,
            start_date=start_date,
            end_date=end_date,
        )
        # Apply pagination manually for date range
        prices = prices[offset : offset + limit]
    else:
        prices = price_repo.get_by_instrument(
            instrument_id=instrument_id,
            limit=limit,
        )

    return [MarketPriceResponse.model_validate(p) for p in prices]


@router.get(
    "/{instrument_id}/latest",
    response_model=MarketPriceResponse | None,
    summary="Get latest price for an instrument",
)
def get_latest_price(
    instrument_id: int,
    instrument_repo: InstrumentRepoDep,
    price_repo: MarketPriceRepoDep,
) -> MarketPriceResponse:
    """Get the most recent price for an instrument.

    Args:
        instrument_id: ID of the instrument.
        instrument_repo: Injected InstrumentRepository.
        price_repo: Injected MarketPriceRepository.

    Returns:
        The most recent market price.

    Raises:
        HTTPException: 404 if instrument not found or no prices exist.
    """
    # Verify instrument exists
    instrument = instrument_repo.get_by_id(instrument_id)
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument with id {instrument_id} not found",
        )

    price = price_repo.get_latest_price(instrument_id)
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prices found for instrument {instrument_id}",
        )

    return MarketPriceResponse.model_validate(price)
