"""Yahoo Finance data transformer.

This module provides the YahooTransformer class for converting
Yahoo Finance API responses to database-ready schemas.

Example::

    transformer = YahooTransformer()
    quote = yahoo_client.get_quote("AAPL")
    if quote:
        market_price = transformer.transform(quote, instrument_id=1)
"""

from decimal import ROUND_HALF_UP, Decimal

from market_data_backend_platform.etl.clients.yahoo import YahooQuoteResponse
from market_data_backend_platform.schemas.market_price import MarketPriceCreate

# Price precision: 4 decimal places is sufficient for market prices
_PRICE_PRECISION = Decimal("0.0001")


class YahooTransformer:
    """Transformer for Yahoo Finance data.

    Converts YahooQuoteResponse objects (from API client) to
    MarketPriceCreate schemas (for database insertion).

    This follows the Interface Segregation Principle (SOLID):
    each data source has its own specialized transformer.

    Example::

        transformer = YahooTransformer()
        prices = yahoo_client.get_historical_prices("AAPL", period="1mo")
        if prices:
            schemas = transformer.transform_batch(prices, instrument_id=1)
    """

    def transform(
        self,
        quote: YahooQuoteResponse,
        instrument_id: int,
    ) -> MarketPriceCreate:
        """Transform a single Yahoo quote to MarketPriceCreate.

        Args:
            quote: The Yahoo Finance quote response.
            instrument_id: Database ID of the instrument.

        Returns:
            MarketPriceCreate schema ready for database insertion.
        """

        def _round(value: Decimal) -> Decimal:
            return value.quantize(_PRICE_PRECISION, rounding=ROUND_HALF_UP)

        return MarketPriceCreate(
            instrument_id=instrument_id,
            timestamp=quote.timestamp,
            open=_round(quote.open),
            high=_round(quote.high),
            low=_round(quote.low),
            close=_round(quote.close),
            volume=quote.volume,
        )

    def transform_batch(
        self,
        quotes: list[YahooQuoteResponse],
        instrument_id: int,
    ) -> list[MarketPriceCreate]:
        """Transform a list of Yahoo quotes to MarketPriceCreate schemas.

        Args:
            quotes: List of Yahoo Finance quote responses.
            instrument_id: Database ID of the instrument.

        Returns:
            List of MarketPriceCreate schemas.
        """
        return [self.transform(quote, instrument_id) for quote in quotes]
