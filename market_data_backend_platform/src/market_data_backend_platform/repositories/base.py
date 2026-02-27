"""Base repository with generic CRUD operations.

This module provides a generic repository base class that can be
extended for specific models. Implements the Repository Pattern.
"""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from market_data_backend_platform.models.base import Base

# Type variable for the model type
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing CRUD operations.

    This base class provides common database operations that can be
    inherited by model-specific repositories.

    Attributes:
        session: SQLAlchemy session for database operations.
        model: The SQLAlchemy model class this repository manages.

    Example::

        class UserRepository(BaseRepository[User]):
            def __init__(self, session: Session):
                super().__init__(session, User)

            def get_by_email(self, email: str) -> User | None:
                return self.session.query(self.model).filter(
                    self.model.email == email
                ).first()
    """

    def __init__(self, session: Session, model: type[ModelType]) -> None:
        """Initialize repository with session and model.

        Args:
            session: SQLAlchemy session for database operations.
            model: The SQLAlchemy model class to manage.
        """
        self.session = session
        self.model = model

    def create(self, obj: ModelType) -> ModelType:
        """Create a new record in the database.

        Args:
            obj: Model instance to persist.

        Returns:
            The persisted model instance with generated fields (id, timestamps).
        """
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, obj_id: int) -> ModelType | None:
        """Get a record by its primary key.

        Args:
            obj_id: Primary key value.

        Returns:
            The model instance if found, None otherwise.
        """
        return self.session.get(self.model, obj_id)

    def get_all(self) -> list[ModelType]:
        """Get all records of this model type.

        Returns:
            List of all model instances.
        """
        return list(self.session.query(self.model).all())

    def update(self, obj: ModelType) -> ModelType:
        """Update an existing record.

        Args:
            obj: Model instance with updated values.

        Returns:
            The updated model instance.
        """
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Delete a record from the database.

        Args:
            obj: Model instance to delete.
        """
        self.session.delete(obj)
        self.session.commit()
