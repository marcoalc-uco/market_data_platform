# Core module
"""Core module containing configuration, logging, and exceptions.

This module provides the foundational components for the application:
- config: Application settings using pydantic-settings
- logging: Structured logging with structlog
- exceptions: Custom exception hierarchy
"""

from .config import Settings, get_settings, settings
from .exceptions import (
    ConfigurationError,
    ExternalAPIError,
    MarketDataError,
    NotFoundError,
    ValidationError,
)
from .logging import get_logger, setup_logging

__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "setup_logging",
    "get_logger",
    "MarketDataError",
    "ConfigurationError",
    "ValidationError",
    "NotFoundError",
    "ExternalAPIError",
]
