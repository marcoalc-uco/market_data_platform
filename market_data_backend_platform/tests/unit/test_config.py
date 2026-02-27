"""Unit tests for the market data backend platform configuration.

These tests validate the loading of variables from `.env`, default values,
and the structure of critical fields such as URLs and API prefix.
"""

import pytest

from market_data_backend_platform.core import Settings, get_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_settings_has_app_name(self) -> None:
        """Test that settings has app_name attribute."""
        settings = Settings()
        assert hasattr(settings, "app_name")
        assert isinstance(settings.app_name, str)

    def test_settings_has_app_version(self) -> None:
        """Test that settings has app_version attribute."""
        settings = Settings()
        assert hasattr(settings, "app_version")
        assert isinstance(settings.app_version, str)

    def test_settings_has_debug(self) -> None:
        """Test that settings has debug attribute."""
        settings = Settings()
        assert hasattr(settings, "debug")
        assert isinstance(settings.debug, bool)

    def test_settings_has_api_prefix(self) -> None:
        """Test that settings has api_prefix attribute."""
        settings = Settings()
        assert hasattr(settings, "api_prefix")
        assert settings.api_prefix.startswith("/")

    def test_settings_has_log_level(self) -> None:
        """Test that settings has log_level attribute."""
        settings = Settings()
        assert hasattr(settings, "log_level")
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_settings_has_log_format(self) -> None:
        """Test that settings has log_format attribute."""
        settings = Settings()
        assert hasattr(settings, "log_format")
        assert settings.log_format in ["json", "console"]


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_get_settings_returns_settings_instance(self) -> None:
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_is_cached(self) -> None:
        """Test that get_settings returns the same cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2


class TestDatabaseSettings:
    """Test cases for database configuration fields."""

    def test_settings_has_db_host(self) -> None:
        """Test that settings has db_host attribute."""
        settings = Settings()
        assert hasattr(settings, "db_host")
        assert isinstance(settings.db_host, str)

    def test_settings_has_db_port(self) -> None:
        """Test that settings has db_port attribute."""
        settings = Settings()
        assert hasattr(settings, "db_port")
        assert isinstance(settings.db_port, int)
        assert 1 <= settings.db_port <= 65535

    def test_settings_has_db_user(self) -> None:
        """Test that settings has db_user attribute."""
        settings = Settings()
        assert hasattr(settings, "db_user")
        assert isinstance(settings.db_user, str)

    def test_settings_has_db_password(self) -> None:
        """Test that settings has db_password attribute."""
        settings = Settings()
        assert hasattr(settings, "db_password")
        # Password should not be empty in production, but can have default for dev
        assert isinstance(settings.db_password, str)

    def test_settings_has_db_name(self) -> None:
        """Test that settings has db_name attribute."""
        settings = Settings()
        assert hasattr(settings, "db_name")
        assert isinstance(settings.db_name, str)

    def test_settings_has_database_url_property(self) -> None:
        """Test that settings has get_database_url method."""
        settings = Settings()
        assert hasattr(settings, "get_database_url")
        url = settings.get_database_url()
        assert url.startswith("postgresql://")
        assert settings.db_host in url
        assert settings.db_name in url

    def test_settings_has_db_pool_size(self) -> None:
        """Test that settings has db_pool_size attribute."""
        settings = Settings()
        assert hasattr(settings, "db_pool_size")
        assert isinstance(settings.db_pool_size, int)
        assert settings.db_pool_size > 0

    def test_settings_has_db_max_overflow(self) -> None:
        """Test that settings has db_max_overflow attribute."""
        settings = Settings()
        assert hasattr(settings, "db_max_overflow")
        assert isinstance(settings.db_max_overflow, int)
        assert settings.db_max_overflow >= 0


class TestSchedulerSettings:
    """Test cases for scheduler configuration fields."""

    def test_settings_has_scheduler_enabled(self) -> None:
        """Test that settings has scheduler_enabled attribute."""
        settings = Settings()
        assert hasattr(settings, "scheduler_enabled")
        assert isinstance(settings.scheduler_enabled, bool)

    def test_settings_has_ingestion_interval_minutes(self) -> None:
        """Test that settings has ingestion_interval_minutes attribute."""
        settings = Settings()
        assert hasattr(settings, "ingestion_interval_minutes")
        assert isinstance(settings.ingestion_interval_minutes, int)
        assert settings.ingestion_interval_minutes >= 1
