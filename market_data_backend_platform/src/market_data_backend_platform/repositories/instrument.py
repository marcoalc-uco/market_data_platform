"""Repository for Instrument model operations.

This module provides database access methods specific to Instrument entities.
"""

from sqlalchemy.orm import Session

from market_data_backend_platform.models.instrument import Instrument, InstrumentType
from market_data_backend_platform.repositories.base import BaseRepository


class InstrumentRepository(BaseRepository[Instrument]):
    """Repository for Instrument CRUD and query operations.

    Extends BaseRepository with Instrument-specific query methods.

    Example::

        repo = InstrumentRepository(session)
        apple = repo.get_by_symbol("AAPL")
        cryptos = repo.get_by_type(InstrumentType.CRYPTO)
    """

    def __init__(self, session: Session) -> None:
        """Initialize repository with session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        super().__init__(session, Instrument)

    def get_by_symbol(self, symbol: str) -> Instrument | None:
        """Get an instrument by its ticker symbol.

        Args:
            symbol: Unique ticker symbol (e.g., "AAPL", "BTC-USD").

        Returns:
            The Instrument if found, None otherwise.
        """
        return (
            self.session.query(Instrument).filter(Instrument.symbol == symbol).first()
        )

    def list_filtered(
        self,
        instrument_type: InstrumentType | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Instrument]:
        """List instruments with optional filters and pagination.

        Args:
            instrument_type: Filter by instrument type (STOCK, INDEX, CRYPTO).
            is_active: Filter by active status. None means no filter.
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            Filtered and paginated list of instruments.
        """
        query = self.session.query(Instrument)
        if instrument_type is not None:
            query = query.filter(Instrument.instrument_type == instrument_type)
        if is_active is not None:
            query = query.filter(Instrument.is_active.is_(is_active))
        return list(query.offset(skip).limit(limit).all())

    def get_active(self) -> list[Instrument]:
        """Get all active instruments.

        Returns:
            List of instruments where is_active is True.
        """
        return list(
            self.session.query(Instrument).filter(Instrument.is_active.is_(True)).all()
        )

    def get_by_type(self, instrument_type: InstrumentType) -> list[Instrument]:
        """Get instruments by their type.

        Args:
            instrument_type: Type filter (STOCK, INDEX, CRYPTO).

        Returns:
            List of instruments matching the specified type.
        """
        return list(
            self.session.query(Instrument)
            .filter(Instrument.instrument_type == instrument_type)
            .all()
        )

    def get_by_exchange(self, exchange: str) -> list[Instrument]:
        """Get instruments traded on a specific exchange.

        Args:
            exchange: Exchange name (e.g., "NASDAQ", "NYSE").

        Returns:
            List of instruments traded on the specified exchange.
        """
        return list(
            self.session.query(Instrument).filter(Instrument.exchange == exchange).all()
        )
