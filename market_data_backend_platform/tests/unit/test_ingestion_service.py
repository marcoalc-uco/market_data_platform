"""Tests for IngestionService.

TDD RED phase: These tests define the expected behavior
of the ingestion service using mocked dependencies.
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from market_data_backend_platform.etl.clients.yahoo import (
    YahooFinanceClient,
    YahooQuoteResponse,
)
from market_data_backend_platform.etl.services.ingestion import IngestionService
from market_data_backend_platform.etl.transformers.yahoo_transformer import (
    YahooTransformer,
)
from market_data_backend_platform.models.instrument import Instrument, InstrumentType
from market_data_backend_platform.models.market_price import MarketPrice
from market_data_backend_platform.repositories.instrument import InstrumentRepository
from market_data_backend_platform.repositories.market_price import MarketPriceRepository


class TestIngestionService:
    """Tests for IngestionService.

    The service orchestrates: Client → Transformer → Repository.
    All dependencies are mocked for unit testing.
    """

    @pytest.fixture
    def mock_instrument_repo(self) -> MagicMock:
        """Create mock InstrumentRepository."""
        return MagicMock(spec=InstrumentRepository)

    @pytest.fixture
    def mock_price_repo(self) -> MagicMock:
        """Create mock MarketPriceRepository."""
        return MagicMock(spec=MarketPriceRepository)

    @pytest.fixture
    def mock_yahoo_client(self) -> MagicMock:
        """Create mock YahooFinanceClient."""
        return MagicMock(spec=YahooFinanceClient)

    @pytest.fixture
    def sample_instrument(self) -> Instrument:
        """Create sample instrument for testing."""
        instrument = MagicMock(spec=Instrument)
        instrument.id = 1
        instrument.symbol = "AAPL"
        instrument.name = "Apple Inc."
        instrument.instrument_type = InstrumentType.STOCK
        return instrument

    @pytest.fixture
    def sample_quotes(self) -> list[YahooQuoteResponse]:
        """Create sample Yahoo quotes for testing."""
        return [
            YahooQuoteResponse(
                symbol="AAPL",
                timestamp=datetime(2024, 1, 15, tzinfo=timezone.utc),
                open=Decimal("185.00"),
                high=Decimal("186.00"),
                low=Decimal("184.50"),
                close=Decimal("185.50"),
                volume=1000000,
                current_price=Decimal("185.50"),
            ),
            YahooQuoteResponse(
                symbol="AAPL",
                timestamp=datetime(2024, 1, 16, tzinfo=timezone.utc),
                open=Decimal("186.00"),
                high=Decimal("187.00"),
                low=Decimal("185.50"),
                close=Decimal("186.50"),
                volume=1100000,
                current_price=Decimal("186.50"),
            ),
        ]

    def test_ingest_by_symbol_success(
        self,
        mock_instrument_repo: MagicMock,
        mock_price_repo: MagicMock,
        mock_yahoo_client: MagicMock,
        sample_instrument: Instrument,
        sample_quotes: list[YahooQuoteResponse],
    ) -> None:
        """Should ingest prices for a symbol.

        Given: A valid symbol exists in the database
        When: We call ingest_by_symbol
        Then: It fetches from Yahoo, transforms, and persists
        """
        # Arrange
        mock_instrument_repo.get_by_symbol.return_value = sample_instrument
        mock_yahoo_client.get_historical_prices.return_value = sample_quotes
        mock_price_repo.bulk_create_new.return_value = [None, None]  # Mock 2 inserted

        service = IngestionService(
            instrument_repo=mock_instrument_repo,
            price_repo=mock_price_repo,
            yahoo_client=mock_yahoo_client,
        )

        # Act
        count = service.ingest_by_symbol("AAPL", period="1mo")

        # Assert
        assert count == 2  # Two quotes ingested
        mock_instrument_repo.get_by_symbol.assert_called_once_with("AAPL")
        mock_yahoo_client.get_historical_prices.assert_called_once_with(
            symbol="AAPL", interval="1d", period="1mo"
        )
        mock_price_repo.bulk_create_new.assert_called_once()

    def test_ingest_by_symbol_instrument_not_found(
        self,
        mock_instrument_repo: MagicMock,
        mock_price_repo: MagicMock,
        mock_yahoo_client: MagicMock,
    ) -> None:
        """Should return 0 if instrument not in database.

        Given: Symbol does not exist in database
        When: We call ingest_by_symbol
        Then: It returns 0 without calling Yahoo API
        """
        # Arrange
        mock_instrument_repo.get_by_symbol.return_value = None

        service = IngestionService(
            instrument_repo=mock_instrument_repo,
            price_repo=mock_price_repo,
            yahoo_client=mock_yahoo_client,
        )

        # Act
        count = service.ingest_by_symbol("UNKNOWN")

        # Assert
        assert count == 0
        mock_yahoo_client.get_historical_prices.assert_not_called()

    def test_ingest_by_symbol_no_data_from_yahoo(
        self,
        mock_instrument_repo: MagicMock,
        mock_price_repo: MagicMock,
        mock_yahoo_client: MagicMock,
        sample_instrument: Instrument,
    ) -> None:
        """Should return 0 if Yahoo returns no data.

        Given: Instrument exists but Yahoo returns None
        When: We call ingest_by_symbol
        Then: It returns 0 and does not persist anything
        """
        # Arrange
        mock_instrument_repo.get_by_symbol.return_value = sample_instrument
        mock_yahoo_client.get_historical_prices.return_value = None

        service = IngestionService(
            instrument_repo=mock_instrument_repo,
            price_repo=mock_price_repo,
            yahoo_client=mock_yahoo_client,
        )

        # Act
        count = service.ingest_by_symbol("AAPL")

        # Assert
        assert count == 0
        mock_price_repo.bulk_create_new.assert_not_called()

    def test_ingest_all_active_iterates_instruments(
        self,
        mock_instrument_repo: MagicMock,
        mock_price_repo: MagicMock,
        mock_yahoo_client: MagicMock,
        sample_quotes: list[YahooQuoteResponse],
    ) -> None:
        """Should ingest prices for all active instruments.

        Given: Multiple active instruments exist
        When: We call ingest_all_active
        Then: It ingests data for each instrument
        """
        # Arrange: Two active instruments
        instrument1 = MagicMock()
        instrument1.id = 1
        instrument1.symbol = "AAPL"

        instrument2 = MagicMock()
        instrument2.id = 2
        instrument2.symbol = "GOOGL"

        mock_instrument_repo.get_active.return_value = [instrument1, instrument2]
        mock_instrument_repo.get_by_symbol.side_effect = [instrument1, instrument2]
        mock_yahoo_client.get_historical_prices.return_value = sample_quotes
        mock_price_repo.bulk_create_new.return_value = [None, None]

        service = IngestionService(
            instrument_repo=mock_instrument_repo,
            price_repo=mock_price_repo,
            yahoo_client=mock_yahoo_client,
        )

        # Act
        result = service.ingest_all_active()

        # Assert
        assert result["total_instruments"] == 2
        assert result["total_inserted"] == 4  # 2 quotes x 2 instruments
        mock_instrument_repo.get_active.assert_called_once()
        assert mock_yahoo_client.get_historical_prices.call_count == 2
