"""Tests for Yahoo Finance client.

Tests use mocked HTTP responses for unit test independence.
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from market_data_backend_platform.etl.clients.yahoo import (
    YahooFinanceClient,
    YahooQuoteResponse,
)


class TestYahooFinanceClient:
    """Tests for YahooFinanceClient."""

    @pytest.fixture
    def client(self):
        """Create Yahoo Finance client instance."""
        return YahooFinanceClient()

    def test_get_quote_success(self, client: YahooFinanceClient):
        """Should return quote data for valid symbol."""
        # Arrange: Mock response
        mock_response = {
            "chart": {
                "result": [
                    {
                        "meta": {
                            "symbol": "AAPL",
                            "regularMarketPrice": 185.50,
                            "currency": "USD",
                        },
                        "timestamp": [1705312800],  # 2024-01-15 10:00:00 UTC
                        "indicators": {
                            "quote": [
                                {
                                    "open": [185.00],
                                    "high": [186.00],
                                    "low": [184.50],
                                    "close": [185.50],
                                    "volume": [1000000],
                                }
                            ]
                        },
                    }
                ],
                "error": None,
            }
        }

        with patch.object(client, "_make_request", return_value=mock_response):
            # Act
            result = client.get_quote("AAPL")

            # Assert
            assert result is not None
            assert result.symbol == "AAPL"
            assert result.current_price == Decimal("185.50")

    def test_get_quote_invalid_symbol(self, client: YahooFinanceClient):
        """Should return None for invalid symbol."""
        # Arrange: Mock error response
        mock_response = {
            "chart": {
                "result": None,
                "error": {"code": "Not Found", "description": "No data found"},
            }
        }

        with patch.object(client, "_make_request", return_value=mock_response):
            # Act
            result = client.get_quote("INVALID_SYMBOL")

            # Assert
            assert result is None

    def test_get_historical_prices_success(self, client: YahooFinanceClient):
        """Should return historical OHLCV data."""
        # Arrange
        mock_response = {
            "chart": {
                "result": [
                    {
                        "meta": {"symbol": "AAPL"},
                        "timestamp": [1705312800, 1705316400],  # 2 timestamps
                        "indicators": {
                            "quote": [
                                {
                                    "open": [185.00, 186.00],
                                    "high": [186.00, 187.00],
                                    "low": [184.50, 185.50],
                                    "close": [185.50, 186.50],
                                    "volume": [1000000, 1100000],
                                }
                            ]
                        },
                    }
                ],
                "error": None,
            }
        }

        with patch.object(client, "_make_request", return_value=mock_response):
            # Act
            result = client.get_historical_prices("AAPL", period="1d")

            # Assert
            assert result is not None
            assert len(result) == 2
            assert result[0].symbol == "AAPL"
            assert result[0].open == Decimal("185.00")
            assert result[0].close == Decimal("185.50")


class TestYahooQuoteResponse:
    """Tests for YahooQuoteResponse data class."""

    def test_quote_response_creation(self):
        """Should create quote response with all fields."""
        quote = YahooQuoteResponse(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
            open=Decimal("185.00"),
            high=Decimal("186.00"),
            low=Decimal("184.50"),
            close=Decimal("185.50"),
            volume=1000000,
            current_price=Decimal("185.50"),
        )

        assert quote.symbol == "AAPL"
        assert quote.open == Decimal("185.00")
        assert quote.volume == 1000000
