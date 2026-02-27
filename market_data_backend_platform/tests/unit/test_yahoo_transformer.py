"""Tests for Yahoo Finance data transformer.

TDD RED phase: These tests define the expected behavior
of the transformer before implementation.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from market_data_backend_platform.etl.clients.yahoo import YahooQuoteResponse
from market_data_backend_platform.etl.transformers.yahoo_transformer import (
    YahooTransformer,
)
from market_data_backend_platform.schemas.market_price import MarketPriceCreate


class TestYahooTransformer:
    """Tests for YahooTransformer.

    The transformer converts YahooQuoteResponse objects to
    MarketPriceCreate schemas for database insertion.
    """

    @pytest.fixture
    def sample_quote(self) -> YahooQuoteResponse:
        """Create a sample Yahoo quote for testing."""
        return YahooQuoteResponse(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
            open=Decimal("185.00"),
            high=Decimal("186.00"),
            low=Decimal("184.50"),
            close=Decimal("185.50"),
            volume=1000000,
            current_price=Decimal("185.50"),
        )

    @pytest.fixture
    def transformer(self) -> YahooTransformer:
        """Create transformer instance."""
        return YahooTransformer()

    def test_transform_single_quote(
        self,
        transformer: YahooTransformer,
        sample_quote: YahooQuoteResponse,
    ) -> None:
        """Should transform a single quote to MarketPriceCreate.

        Given: A YahooQuoteResponse with OHLCV data
        When: We transform it with an instrument_id
        Then: We get a valid MarketPriceCreate schema
        """
        # Arrange
        instrument_id = 1

        # Act
        result = transformer.transform(sample_quote, instrument_id)

        # Assert
        assert isinstance(result, MarketPriceCreate)
        assert result.instrument_id == instrument_id
        assert result.timestamp == sample_quote.timestamp
        assert result.open == sample_quote.open
        assert result.high == sample_quote.high
        assert result.low == sample_quote.low
        assert result.close == sample_quote.close
        assert result.volume == sample_quote.volume

    def test_transform_batch(
        self,
        transformer: YahooTransformer,
        sample_quote: YahooQuoteResponse,
    ) -> None:
        """Should transform a list of quotes.

        Given: A list of YahooQuoteResponse objects
        When: We transform them with an instrument_id
        Then: We get a list of MarketPriceCreate schemas
        """
        # Arrange
        quotes = [sample_quote, sample_quote]  # Two quotes
        instrument_id = 1

        # Act
        results = transformer.transform_batch(quotes, instrument_id)

        # Assert
        assert len(results) == 2
        assert all(isinstance(r, MarketPriceCreate) for r in results)
        assert all(r.instrument_id == instrument_id for r in results)

    def test_transform_with_zero_values(
        self,
        transformer: YahooTransformer,
    ) -> None:
        """Should handle quotes with zero values.

        Note: Zero values can occur on market holidays or
        when data is unavailable. We should still transform them.
        """
        # Arrange
        quote = YahooQuoteResponse(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 15, tzinfo=timezone.utc),
            open=Decimal("0"),
            high=Decimal("0"),
            low=Decimal("0"),
            close=Decimal("0"),
            volume=0,
            current_price=Decimal("0"),
        )

        # Act
        result = transformer.transform(quote, instrument_id=1)

        # Assert
        assert result.open == Decimal("0")
        assert result.volume == 0
