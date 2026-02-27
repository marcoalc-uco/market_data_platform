"""FastAPI dependency injection utilities.

This module provides shared dependencies for API endpoints.
Dependencies are injected using FastAPI's Depends() mechanism.

Example usage::

    from market_data_backend_platform.api.dependencies import SessionDep

    @router.get("/example")
    async def example(session: SessionDep):
        instruments = session.query(Instrument).all()
        return instruments
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from market_data_backend_platform.core import Settings, get_settings
from market_data_backend_platform.db.session import SessionLocal
from market_data_backend_platform.repositories import (
    InstrumentRepository,
    MarketPriceRepository,
)

# Type alias for settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session for request lifecycle.

    Creates a new session for each request and ensures proper cleanup.

    Yields:
        Session: SQLAlchemy session bound to the engine.

    Example::

        @router.get("/items")
        def get_items(session: SessionDep):
            return session.query(Item).all()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Type alias for session dependency
SessionDep = Annotated[Session, Depends(get_db_session)]


def get_instrument_repository(session: SessionDep) -> InstrumentRepository:
    """Create InstrumentRepository with injected session.

    Args:
        session: Database session from dependency injection.

    Returns:
        InstrumentRepository instance.
    """
    return InstrumentRepository(session)


def get_market_price_repository(session: SessionDep) -> MarketPriceRepository:
    """Create MarketPriceRepository with injected session.

    Args:
        session: Database session from dependency injection.

    Returns:
        MarketPriceRepository instance.
    """
    return MarketPriceRepository(session)


# Type aliases for repository dependencies
InstrumentRepoDep = Annotated[InstrumentRepository, Depends(get_instrument_repository)]
MarketPriceRepoDep = Annotated[
    MarketPriceRepository,
    Depends(get_market_price_repository),
]
