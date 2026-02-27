"""Unit tests for custom exceptions.

These tests validate the exception hierarchy and behavior.
"""

import pytest

from market_data_backend_platform.core import (
    ConfigurationError,
    ExternalAPIError,
    MarketDataError,
    NotFoundError,
    ValidationError,
)


class TestMarketDataError:
    """Test cases for the base MarketDataError exception.

    MarketDataError is the base class for all custom exceptions.
    It stores a message and optional details dict for structured error info.
    """

    def test_can_be_raised(self) -> None:
        """Test that MarketDataError can be raised."""
        with pytest.raises(MarketDataError):
            raise MarketDataError("Something went wrong")

    def test_has_message_attribute(self) -> None:
        """Test that exception stores the message."""
        exc = MarketDataError("Test error message")
        assert exc.message == "Test error message"

    def test_has_details_attribute(self) -> None:
        """Test that exception stores optional details."""
        details = {"key": "value", "code": 123}
        exc = MarketDataError("Error", details=details)
        assert exc.details == details

    def test_details_defaults_to_empty_dict(self) -> None:
        """Test that details defaults to empty dict when not provided."""
        exc = MarketDataError("Error")
        assert exc.details == {}

    def test_str_returns_message(self) -> None:
        """Test that str(exception) returns the message."""
        exc = MarketDataError("My error message")
        assert str(exc) == "My error message"


class TestConfigurationError:
    """Test cases for ConfigurationError.

    Used when there's an issue with application configuration
    (e.g., missing .env file, invalid settings).
    """

    def test_inherits_from_market_data_error(self) -> None:
        """Test that ConfigurationError inherits from MarketDataError."""
        exc = ConfigurationError("Config error")
        assert isinstance(exc, MarketDataError)

    def test_can_be_caught_as_base_exception(self) -> None:
        """Test that it can be caught as MarketDataError."""
        with pytest.raises(MarketDataError):
            raise ConfigurationError("Missing DATABASE_URL")


class TestValidationError:
    """Test cases for ValidationError.

    Used when input data fails validation
    (e.g., invalid date format, missing required field).
    """

    def test_inherits_from_market_data_error(self) -> None:
        """Test that ValidationError inherits from MarketDataError."""
        exc = ValidationError("Invalid data")
        assert isinstance(exc, MarketDataError)

    def test_stores_message_and_details(self) -> None:
        """Test that it stores validation error details."""
        exc = ValidationError(
            "Validation failed", details={"field": "date", "error": "invalid format"}
        )
        assert exc.message == "Validation failed"
        assert exc.details["field"] == "date"


class TestNotFoundError:
    """Test cases for NotFoundError.

    Used when a requested resource doesn't exist
    (e.g., instrument not found, price data not available).
    """

    def test_inherits_from_market_data_error(self) -> None:
        """Test that NotFoundError inherits from MarketDataError."""
        exc = NotFoundError("Resource not found")
        assert isinstance(exc, MarketDataError)

    def test_stores_resource_info_in_details(self) -> None:
        """Test that details can store resource information."""
        exc = NotFoundError(
            "Instrument not found", details={"symbol": "INVALID", "type": "stock"}
        )
        assert exc.details["symbol"] == "INVALID"


class TestExternalAPIError:
    """Test cases for ExternalAPIError.

    Used when an external API call fails
    (e.g., Yahoo Finance API timeout, rate limit).
    Includes optional status_code for HTTP errors.
    """

    def test_inherits_from_market_data_error(self) -> None:
        """Test that ExternalAPIError inherits from MarketDataError."""
        exc = ExternalAPIError("API call failed")
        assert isinstance(exc, MarketDataError)

    def test_has_status_code_attribute(self) -> None:
        """Test that it stores HTTP status code."""
        exc = ExternalAPIError("Rate limited", status_code=429)
        assert exc.status_code == 429

    def test_status_code_defaults_to_none(self) -> None:
        """Test that status_code is None when not provided."""
        exc = ExternalAPIError("Connection timeout")
        assert exc.status_code is None

    def test_stores_api_details(self) -> None:
        """Test that details can store API-specific info."""
        exc = ExternalAPIError(
            "API error",
            status_code=503,
            details={"api": "yahoo_finance", "endpoint": "/v8/finance/quote"},
        )
        assert exc.status_code == 503
        assert exc.details["api"] == "yahoo_finance"
