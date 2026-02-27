"""Yahoo Finance API client.

This module provides a client for fetching market data from Yahoo Finance.
Uses the free Yahoo Finance API (no API key required).

Example::

    client = YahooFinanceClient()
    quote = client.get_quote("AAPL")
    if quote:
        print(f"Current price: {quote.current_price}")
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx

from market_data_backend_platform.core import get_logger

logger = get_logger(__name__)

# Yahoo Finance API base URL
YAHOO_API_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"


@dataclass
class YahooQuoteResponse:
    """Data class for Yahoo Finance quote response.

    Attributes:
        symbol: Stock symbol (e.g., "AAPL").
        timestamp: Quote timestamp.
        open: Opening price.
        high: High price.
        low: Low price.
        close: Closing price.
        volume: Trading volume.
        current_price: Current market price.
    """

    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    current_price: Decimal


class YahooFinanceClient:
    """Client for Yahoo Finance API.

    Fetches real-time quotes and historical OHLCV data.

    Example::

        client = YahooFinanceClient()

        # Get current quote
        quote = client.get_quote("AAPL")

        # Get historical data
        prices = client.get_historical_prices("AAPL", period="1mo")
    """

    def __init__(self, timeout: float = 10.0) -> None:
        """Initialize the client.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout

    def _make_request(
        self,
        symbol: str,
        interval: str = "1d",
        period: str = "1d",
    ) -> dict[str, Any]:
        """Make HTTP request to Yahoo Finance API.

        Args:
            symbol: Stock symbol.
            interval: Data interval (1m, 5m, 1h, 1d, 1wk, 1mo).
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max).

        Returns:
            JSON response as dictionary.
        """
        url = f"{YAHOO_API_BASE}/{symbol}"
        params = {
            "interval": interval,
            "range": period,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()  # type: ignore[no-any-return]
        except httpx.HTTPError as e:
            logger.error("yahoo_api_error", symbol=symbol, error=str(e))
            return {"chart": {"result": None, "error": {"description": str(e)}}}

    def get_quote(self, symbol: str) -> YahooQuoteResponse | None:
        """Get current quote for a symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL", "GOOGL").

        Returns:
            YahooQuoteResponse if successful, None if symbol not found.
        """
        data = self._make_request(symbol, interval="1d", period="1d")

        result = data.get("chart", {}).get("result")
        if not result:
            logger.warning("yahoo_quote_not_found", symbol=symbol)
            return None

        try:
            chart = result[0]
            meta = chart.get("meta", {})
            quotes = chart.get("indicators", {}).get("quote", [{}])[0]
            timestamps = chart.get("timestamp", [])

            if not timestamps:
                return None

            # Get the latest data point
            idx = -1  # Last element
            timestamp = datetime.fromtimestamp(timestamps[idx], tz=timezone.utc)

            return YahooQuoteResponse(
                symbol=meta.get("symbol", symbol),
                timestamp=timestamp,
                open=Decimal(str(quotes.get("open", [0])[idx] or 0)),
                high=Decimal(str(quotes.get("high", [0])[idx] or 0)),
                low=Decimal(str(quotes.get("low", [0])[idx] or 0)),
                close=Decimal(str(quotes.get("close", [0])[idx] or 0)),
                volume=int(quotes.get("volume", [0])[idx] or 0),
                current_price=Decimal(str(meta.get("regularMarketPrice", 0))),
            )
        except (IndexError, KeyError, TypeError) as e:
            logger.error("yahoo_parse_error", symbol=symbol, error=str(e))
            return None

    def get_historical_prices(
        self,
        symbol: str,
        interval: str = "1d",
        period: str = "1mo",
    ) -> list[YahooQuoteResponse] | None:
        """Get historical OHLCV data for a symbol.

        Args:
            symbol: Stock symbol.
            interval: Data interval (1d, 1wk, 1mo).
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max).

        Returns:
            List of YahooQuoteResponse objects, or None if error.
        """
        data = self._make_request(symbol, interval=interval, period=period)

        result = data.get("chart", {}).get("result")
        if not result:
            logger.warning("yahoo_historical_not_found", symbol=symbol)
            return None

        try:
            chart = result[0]
            meta = chart.get("meta", {})
            quotes = chart.get("indicators", {}).get("quote", [{}])[0]
            timestamps = chart.get("timestamp", [])

            if not timestamps:
                return None

            responses = []
            for i, ts in enumerate(timestamps):
                open_val = Decimal(str(quotes.get("open", [])[i] or 0))
                high_val = Decimal(str(quotes.get("high", [])[i] or 0))
                low_val = Decimal(str(quotes.get("low", [])[i] or 0))
                close_val = Decimal(str(quotes.get("close", [])[i] or 0))
                vol_val = int(quotes.get("volume", [])[i] or 0)

                # Skip empty or 0-price candles
                if open_val == 0 and close_val == 0:
                    continue

                # Skip completely flat candles with 0 volume (often live incomplete ticks or illiquid periods)
                if (
                    vol_val == 0
                    and open_val == close_val
                    and high_val == low_val
                    and open_val == high_val
                ):
                    continue

                timestamp = datetime.fromtimestamp(ts, tz=timezone.utc)

                response = YahooQuoteResponse(
                    symbol=meta.get("symbol", symbol),
                    timestamp=timestamp,
                    open=open_val,
                    high=high_val,
                    low=low_val,
                    close=close_val,
                    volume=vol_val,
                    current_price=Decimal(str(meta.get("regularMarketPrice", 0))),
                )
                responses.append(response)

            return responses
        except (IndexError, KeyError, TypeError) as e:
            logger.error("yahoo_parse_error", symbol=symbol, error=str(e))
            return None
