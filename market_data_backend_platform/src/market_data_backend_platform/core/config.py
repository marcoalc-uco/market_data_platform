"""Application configuration using pydantic-settings.

This module provides centralized configuration management for the application.
Settings are loaded from environment variables and .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        app_name: Name of the application.
        app_version: Current version of the application.
        debug: Enable debug mode (more verbose logging, etc.).
        api_prefix: URL prefix for all API routes.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Log output format ("json" for production, "console" for dev).
        db_host: PostgreSQL host address.
        db_port: PostgreSQL port (1-65535).
        db_user: PostgreSQL username.
        db_password: PostgreSQL password (hidden from repr).
        db_name: PostgreSQL database name.
        db_pool_size: Connection pool size.
        db_max_overflow: Maximum overflow connections.
        database_url: Full PostgreSQL URL; overrides individual db_* fields if set.
        secret_key: HMAC secret for signing JWT tokens (hidden from repr).
        access_token_expire_minutes: JWT lifetime in minutes.
        admin_email: Email of the single admin user allowed to log in.
        admin_password_hash: Bcrypt hash of the admin password (hidden from repr).
        scheduler_enabled: Enable automated data-ingestion scheduler on startup.
        ingestion_interval_minutes: Interval between ingestion runs in minutes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Market Data Backend Platform"
    app_version: str = "0.1.0"
    debug: bool = False

    # API
    api_prefix: str = "/api/v1"

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "console"] = "console"

    # Database - PostgreSQL
    db_host: str = Field(
        default="localhost",
        description="PostgreSQL host address",
    )
    db_port: int = Field(
        default=5432,
        ge=1,
        le=65535,
        description="PostgreSQL port number",
    )
    db_user: str = Field(
        default="postgres",
        description="PostgreSQL username",
    )
    db_password: str = Field(
        default="",
        repr=False,  # Hide password in logs/repr
        description="PostgreSQL password",
    )
    db_name: str = Field(
        default="market_data",
        description="PostgreSQL database name",
    )

    # Connection pool settings
    db_pool_size: int = Field(
        default=5,
        ge=1,
        description="Database connection pool size",
    )
    db_max_overflow: int = Field(
        default=10,
        ge=0,
        description="Maximum overflow connections beyond pool size",
    )

    # Auth - JWT
    secret_key: str = Field(
        default="changeme-generate-with-openssl-rand-hex-32",
        repr=False,
        description="Secret key for signing JWT tokens",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        description="JWT access token lifetime in minutes",
    )
    admin_email: str = Field(
        default="admin@market.com",
        description="Admin user email for login",
    )
    admin_password_hash: str = Field(
        default="$2b$12$B9NxCdpM3Tz3YnxkXTqaw.trJaR.lz0bz9uzK5X56Au2FVuV23aLG",
        repr=False,
        description="Bcrypt hash of admin password (set via ADMIN_PASSWORD_HASH env var)",
    )

    # Scheduler
    ingestion_interval_minutes: int = Field(
        default=5,
        ge=1,
        description="Interval in minutes between automated ingestion runs",
    )
    scheduler_enabled: bool = Field(
        default=True,
        description="Enable automated data ingestion scheduler",
    )

    # Database URL (optional - if set, overrides computed URL)
    database_url: str | None = Field(
        default=None,
        description="Full PostgreSQL connection URL (overrides individual fields if set)",
    )

    def get_database_url(self) -> str:
        """Get the database URL.

        Returns pre-configured DATABASE_URL if set (for Docker),
        otherwise constructs from individual fields (for local dev).

        Returns:
            str: PostgreSQL connection string
        """
        if self.database_url:
            return self.database_url

        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses lru_cache to ensure only one Settings instance is created,
    avoiding multiple reads of environment variables.

    Returns:
        Settings: Cached application settings.
    """
    return Settings()


# Convenience instance for direct import
settings = get_settings()
