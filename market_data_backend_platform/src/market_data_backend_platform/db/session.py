"""SQLAlchemy database engine and session configuration.

This module provides the database engine and session factory
for the application. It uses the configuration from core.config.

Usage with FastAPI dependency injection:
    @app.get("/items")
    def get_items(session: Session = Depends(get_session)):
        ...
"""

from collections.abc import Generator
from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from market_data_backend_platform.core import settings

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

# Database engine with connection pooling
engine: "Engine" = create_engine(
    settings.get_database_url(),  # Use method to get URL (supports Docker override)
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.debug,  # Log SQL in debug mode
)

# Session factory - creates new sessions bound to the engine
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_session() -> Generator[Session, None, None]:
    """Provide a database session for FastAPI dependency injection.

    This generator creates a new session for each request and
    ensures proper cleanup after the request completes.

    Yields:
        Session: SQLAlchemy session bound to the engine.

    Example ::
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            items = session.query(Item).all()
            return items
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_test_session_factory() -> "tuple[Engine, sessionmaker[Session]]":
    """Create an engine and session factory for testing with SQLite in-memory.

    Returns both the engine and the session factory so the caller can call
    ``engine.dispose()`` after the test, preventing ResourceWarning about
    unclosed SQLite connections.

    Returns:
        Tuple of (engine, sessionmaker) bound to an in-memory SQLite database.

    Example::
        engine, factory = create_test_session_factory()
        try:
            session = factory()
            ...
        finally:
            engine.dispose()
    """
    test_engine = create_engine("sqlite:///:memory:")
    factory = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
    )
    return test_engine, factory
