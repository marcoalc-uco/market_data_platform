"""Custom exceptions for the Market Data Backend Platform.

This module provides a hierarchy of exceptions for structured error handling:

    MarketDataError (base)
    ├── ConfigurationError    # Settings/env issues
    ├── ValidationError       # Invalid input data
    ├── NotFoundError         # Resource not found
    └── ExternalAPIError      # External API failures

Usage:
    from market_data_backend_platform.core import NotFoundError

    raise NotFoundError(
        "Instrument not found",
        details={"symbol": "INVALID", "type": "stock"}
    )
"""

from typing import Any


class MarketDataError(Exception):
    """Base exception for all Market Data Backend Platform errors.

    All custom exceptions inherit from this class, allowing:
    - Catching all application errors with `except MarketDataError`
    - Structured error info via `message` and `details`
    - Easy logging with `logger.error(exc.message, **exc.details)`

    Attributes:
        message: Error description.
        details: Optional dict with structured error context.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error description.
            details: Optional dictionary with additional error context.
                     Useful for logging and debugging.
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(MarketDataError):
    """Exception raised for configuration errors.

    Use when:
    - Required environment variable is missing
    - Invalid value in .env or settings
    - Database connection string is malformed

    Example:
        raise ConfigurationError(
            "Missing required setting",
            details={"setting": "DATABASE_URL"}
        )
    """


class ValidationError(MarketDataError):
    """Exception raised for data validation errors.

    Use when:
    - Request body has invalid format
    - Query parameter fails validation
    - Date range is invalid

    Example:
        raise ValidationError(
            "Invalid date format",
            details={
                "field": "start_date",
                "expected": "YYYY-MM-DD",
                "received": "2024/01/01",
            }
        )
    """


class NotFoundError(MarketDataError):
    """Exception raised when a requested resource is not found.

    Use when:
    - Instrument symbol doesn't exist
    - No price data for given date range
    - User/record not found in database

    Example:
        raise NotFoundError(
            "Instrument not found",
            details={"symbol": "INVALID", "searched_in": "yahoo_finance"}
        )
    """


class ExternalAPIError(MarketDataError):
    """Exception raised for external API failures.

    Use when:
    - Yahoo Finance API returns error
    - Connection timeout to external service
    - Rate limit exceeded

    Includes optional `status_code` for HTTP error codes.

    Attributes:
        status_code: HTTP status code from external API (e.g., 429, 503).

    Example:
        raise ExternalAPIError(
            "Yahoo Finance rate limit exceeded",
            status_code=429,
            details={"api": "yahoo_finance", "retry_after": 60}
        )
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            status_code: Optional HTTP status code from external API.
            details: Optional dictionary with additional error context.
        """
        super().__init__(message, details)
        self.status_code = status_code
