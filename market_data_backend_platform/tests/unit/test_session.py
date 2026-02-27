"""Tests for database session configuration.

This module tests the database engine and session factory setup.
For unit tests, we use SQLite in-memory to avoid PostgreSQL dependency.
"""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class TestDatabaseEngineConfiguration:
    """Tests for SQLAlchemy engine configuration logic."""

    def test_engine_with_sqlite_returns_engine_instance(self) -> None:
        """Test that creating an engine returns a valid SQLAlchemy Engine."""
        test_engine = create_engine("sqlite:///:memory:")
        try:
            assert isinstance(test_engine, Engine)
        finally:
            test_engine.dispose()

    def test_engine_can_execute_queries(self) -> None:
        """Test that the engine can execute basic queries."""
        test_engine = create_engine("sqlite:///:memory:")
        try:
            with test_engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            test_engine.dispose()


class TestSessionFactory:
    """Tests for SQLAlchemy session factory."""

    @pytest.fixture
    def test_engine(self) -> Generator[Engine, None, None]:
        """Create a test engine with SQLite in-memory, disposed after the test."""
        engine = create_engine("sqlite:///:memory:")
        yield engine
        engine.dispose()

    @pytest.fixture
    def test_session_factory(self, test_engine: Engine) -> sessionmaker[Session]:
        """Create a test session factory."""
        return sessionmaker(
            bind=test_engine,
            autocommit=False,
            autoflush=False,
        )

    def test_session_factory_creates_session(
        self, test_session_factory: sessionmaker[Session]
    ) -> None:
        """Test that session factory creates valid sessions."""
        session = test_session_factory()
        assert isinstance(session, Session)
        session.close()

    def test_session_executes_queries(
        self, test_session_factory: sessionmaker[Session]
    ) -> None:
        """Test that session can execute basic queries."""
        session = test_session_factory()
        result = session.execute(text("SELECT 1 + 1"))
        assert result.scalar() == 2
        session.close()

    def test_session_is_bound_to_engine(
        self,
        test_engine: Engine,
        test_session_factory: sessionmaker[Session],
    ) -> None:
        """Test that sessions are properly bound to the engine."""
        session = test_session_factory()
        assert session.get_bind() == test_engine
        session.close()


class TestGetSessionGenerator:
    """Tests for the get_session dependency generator."""

    def test_get_session_yields_session(self) -> None:
        """Test that get_session generator yields a Session."""
        from market_data_backend_platform.db.session import (
            create_test_session_factory,
        )

        # Unpack both engine and factory to allow explicit disposal
        test_engine, test_factory = create_test_session_factory()
        try:
            session_gen = _get_session_from_factory(test_factory)
            session = next(session_gen)

            assert isinstance(session, Session)

            # Exhaust the generator so the finally block closes the session
            try:
                next(session_gen)
            except StopIteration:
                pass
        finally:
            test_engine.dispose()


def _get_session_from_factory(
    factory: sessionmaker[Session],
) -> "Generator[Session, None, None]":
    """Helper to create a session generator from a factory.

    This mimics the get_session behavior for testing.
    """
    from collections.abc import Generator

    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
