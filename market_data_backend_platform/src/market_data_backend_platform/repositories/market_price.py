"""Repository for MarketPrice model operations.

This module provides database access methods specific to MarketPrice entities.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from market_data_backend_platform.models.market_price import MarketPrice
from market_data_backend_platform.repositories.base import BaseRepository


class MarketPriceRepository(BaseRepository[MarketPrice]):
    """Repository for MarketPrice CRUD and query operations.

    Extends BaseRepository with MarketPrice-specific query methods.

    Example::

        repo = MarketPriceRepository(session)
        prices = repo.get_by_instrument(instrument_id=1)
        latest = repo.get_latest_price(instrument_id=1)
    """

    def __init__(self, session: Session) -> None:
        """Initialize repository with session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        super().__init__(session, MarketPrice)

    def get_by_instrument(
        self,
        instrument_id: int,
        limit: int | None = None,
    ) -> list[MarketPrice]:
        """Get price records for a specific instrument.

        Args:
            instrument_id: ID of the instrument.
            limit: Optional maximum number of records to return.

        Returns:
            List of MarketPrice records ordered by timestamp descending.
        """
        query = (
            self.session.query(MarketPrice)
            .filter(MarketPrice.instrument_id == instrument_id)
            .order_by(MarketPrice.timestamp.desc())
        )
        if limit:
            query = query.limit(limit)
        return list(query.all())

    def get_latest_price(self, instrument_id: int) -> MarketPrice | None:
        """Get the most recent price for an instrument.

        Args:
            instrument_id: ID of the instrument.

        Returns:
            The most recent MarketPrice if exists, None otherwise.
        """
        return (
            self.session.query(MarketPrice)
            .filter(MarketPrice.instrument_id == instrument_id)
            .order_by(MarketPrice.timestamp.desc())
            .first()
        )

    def get_by_date_range(
        self,
        instrument_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> list[MarketPrice]:
        """Get price records within a date range.

        Args:
            instrument_id: ID of the instrument.
            start_date: Start of the date range (inclusive).
            end_date: End of the date range (inclusive).

        Returns:
            List of MarketPrice records within the range.
        """
        return list(
            self.session.query(MarketPrice)
            .filter(
                MarketPrice.instrument_id == instrument_id,
                MarketPrice.timestamp >= start_date,
                MarketPrice.timestamp <= end_date,
            )
            .order_by(MarketPrice.timestamp.asc())
            .all()
        )

    def bulk_create(self, prices: list[MarketPrice]) -> list[MarketPrice]:
        """Create multiple price records efficiently.

        Args:
            prices: List of MarketPrice instances to persist.

        Returns:
            The persisted MarketPrice instances.
        """
        self.session.add_all(prices)
        self.session.commit()
        for price in prices:
            self.session.refresh(price)
        return prices

    def get_existing_timestamps(
        self,
        instrument_id: int,
        timestamps: list[datetime],
    ) -> set[datetime]:
        """Get timestamps that already exist in the database.

        This is used for idempotent insertion to avoid duplicates.

        Args:
            instrument_id: ID of the instrument.
            timestamps: List of timestamps to check.

        Returns:
            Set of timestamps that already exist in the database.
        """
        if not timestamps:
            return set()

        existing = (
            self.session.query(MarketPrice.timestamp)
            .filter(
                MarketPrice.instrument_id == instrument_id,
                MarketPrice.timestamp.in_(timestamps),
            )
            .all()
        )
        return {row[0] for row in existing}

    def bulk_create_new(self, prices: list[MarketPrice]) -> list[MarketPrice]:
        """Create only prices that don't already exist (idempotent).

        Filters out prices with timestamps that already exist for the
        same instrument, then inserts only the new ones.

        Args:
            prices: List of MarketPrice instances to potentially persist.

        Returns:
            Only the newly inserted MarketPrice instances.
        """
        if not prices:
            return []

        # Group by instrument_id to check each separately
        instrument_id = prices[0].instrument_id
        timestamps = [p.timestamp for p in prices]

        # Get existing timestamps
        existing = self.get_existing_timestamps(instrument_id, timestamps)

        # Filter to only new prices
        new_prices = [p for p in prices if p.timestamp not in existing]

        if not new_prices:
            return []

        return self.bulk_create(new_prices)
