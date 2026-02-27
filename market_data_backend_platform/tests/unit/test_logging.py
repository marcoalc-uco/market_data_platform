"""Unit tests for the market data backend platform logging.

These tests validate the structlog configuration and logging getter.
"""

import pytest
import structlog

from market_data_backend_platform.core import get_logger, setup_logging


class TestSetupLogging:
    """Test cases for setup_logging function.

    setup_logging() configures structlog with processors based on settings.
    It should be called once at application startup.
    """

    def test_setup_logging_does_not_raise(self) -> None:
        """Test that setup_logging can be called without errors."""
        # Should not raise any exception
        setup_logging()

    def test_setup_logging_can_be_called_multiple_times(self) -> None:
        """Test that setup_logging is idempotent (safe to call multiple times)."""
        setup_logging()
        setup_logging()  # Should not raise


class TestGetLogger:
    """Test cases for get_logger function.

    get_logger() returns a configured structlog logger instance.
    Can optionally receive a name for the logger.
    """

    def test_get_logger_returns_bound_logger(self) -> None:
        """Test that get_logger returns a structlog BoundLogger."""
        setup_logging()
        logger = get_logger()
        # Should be a bound logger (can call .info(), .error(), etc.)
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "debug")

    def test_get_logger_with_name(self) -> None:
        """Test that get_logger accepts a name parameter."""
        setup_logging()
        logger = get_logger("my_module")
        # Should not raise and should return a logger
        assert hasattr(logger, "info")

    def test_get_logger_can_log_message(self) -> None:
        """Test that the logger can actually log a message."""
        setup_logging()
        logger = get_logger("test")
        # Should not raise when logging
        logger.info("test message", key="value")

    def test_get_logger_can_log_with_context(self) -> None:
        """Test that logger supports structured context (key-value pairs)."""
        setup_logging()
        logger = get_logger("test")
        # Structlog allows binding context
        logger_with_context = logger.bind(user_id=123)
        logger_with_context.info("action performed")
