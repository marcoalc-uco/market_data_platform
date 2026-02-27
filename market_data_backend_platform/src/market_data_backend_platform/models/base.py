"""SQLAlchemy model base classes and mixins.

This module provides the declarative base class and common mixins
for all database models in the application.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    All models should inherit from this class to use the ORM features.
    Each model must define its own ``__tablename__`` explicitly to specify
    the database table name.

    **Note**:
        The ``type: ignore[misc]`` comment is needed because mypy doesn't
        fully understand SQLAlchemy's metaprogramming.

    Example
    -------
    ::
        from sqlalchemy import String, create_engine
        from sqlalchemy.orm import Mapped, mapped_column
        from market_data_backend_platform.models import Base

        class User(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
            email: Mapped[str] = mapped_column(String(100), unique=True)

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
    """


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns.

    Use this mixin for models that need to track creation and update times.
    The timestamps are set automatically by the database.

    Attributes:
        created_at: Timestamp when the record was created (auto-set).
        updated_at: Timestamp when the record was last updated (auto-set).

    Example::

        class User(TimestampMixin, Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
