"""Structured logging configuration using structlog.

This module provides:
- setup_logging(): Configures structlog based on settings (json/console format)
- get_logger(): Returns a configured logger instance

Should be called once at application startup via setup_logging().
"""

import logging
import sys
from typing import Any

import structlog

from market_data_backend_platform.core.config import get_settings


def setup_logging() -> None:
    """Configure structured logging with structlog.

    Reads log_level and log_format from settings to determine:
    - Log level threshold (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Output format ("json" for production, "console" for development)

    This function is idempotent - safe to call multiple times.
    """
    settings = get_settings()

    # Convert string log level to logging constant
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure standard library logging (used as fallback)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
        force=True,  # Override any existing configuration
    )

    # Shared processors for all outputs
    # Processors are functions that transform log entries
    shared_processors: list[Any] = [
        # Add log level to the event dict
        structlog.stdlib.add_log_level,
        # Add timestamp in ISO format
        structlog.processors.TimeStamper(fmt="iso"),
        # Handle positional arguments in log calls
        structlog.stdlib.PositionalArgumentsFormatter(),
        # Render stack info if present
        structlog.processors.StackInfoRenderer(),
        # Ensure all strings are unicode
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "json":
        # JSON output for production
        # Good for: Grafana Loki, ELK Stack, CloudWatch
        final_processors: list[Any] = [
            *shared_processors,
            # Format exception info as string
            structlog.processors.format_exc_info,
            # Render as JSON
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console output for development
        final_processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=final_processors,
        # Create a filtering logger at the specified level
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        # Use dict as context class
        context_class=dict,
        # Use PrintLoggerFactory to output to stdout
        logger_factory=structlog.PrintLoggerFactory(),
        # Cache the logger for performance
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Optional name for the logger (typically __name__ of the module).
              Used to identify the source of log messages.

    Returns:
        A structlog BoundLogger that supports:
        - logger.info("message", key=value)
        - logger.error("message", key=value)
        - logger.bind(key=value) for adding context

    Example:
        logger = get_logger(__name__)
        logger.info("user_login", user_id=123, ip="192.168.1.1")
    """
    return structlog.get_logger(name)
