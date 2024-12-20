"""
Contains a generic base repository or DAO for access patterns to data for a given database model
"""

from datetime import datetime, UTC
from typing import (
    Generic,
    Any,
    Optional,
    Sequence,
    Type,
    TypeVar,
    cast,
    TypeGuard,
    Union,
)
from sqlalchemy import ColumnElement, Select, select

from sanctumlabs_dbkit.exceptions import ModelNotFoundError
from sanctumlabs_dbkit.sql.models import AbstractBaseModel, BaseOutboxEvent
from sanctumlabs_dbkit.sql.session import Session
from sanctumlabs_dbkit.exceptions import UnsupportedModelOperationError

RepositoryBaseModel = Union[AbstractBaseModel, BaseOutboxEvent]

T = TypeVar("T", bound=RepositoryBaseModel)


class Repository(Generic[T]):
    """
    A base class for implementing a Repository or DAO.

    ```python
    job_dao = Repository(model=Job, session=session)

    job = job_dao.find("123")
    """

    def __init__(self, model: Type[T], session: Session) -> None:
        """Creates an instance of the Repository"""
        self.model = model
        self.session = session

    @staticmethod
    def _supports_soft_deletion(model: Type[T]) -> TypeGuard[Type[AbstractBaseModel]]:
        """
        Indicates if the provided model supports soft deletion (has a 'deleted_at' column). This function
        takes in an argument due to mypy typeguarding requirements, and is thus static.
        """
        return issubclass(model, AbstractBaseModel)

    def create(self, refresh: bool = False, **kwargs: Any) -> T:
        """Creates a new entity

        Args:
            refresh (bool, optional): whether to refresh the model with the data in the return. Defaults to False.

        Returns:
            T: The created model instance
        """
        model_instance = self.model(**kwargs)
        self.session.add(model_instance)

        if refresh:
            self.session.flush()
            self.session.refresh(model_instance)

        return cast(T, model_instance)

    def query(self, include_deleted: bool = False) -> Select:
        """Returns a select query with the model including deleted records if the include_deleted is set to True"""
        selectable = select(self.model)

        if not include_deleted and self._supports_soft_deletion(self.model):
            selectable = selectable.where(
                self.model.deleted_at == self.model.not_deleted_value()
            )

        return selectable

    def find(self, pk: Any, include_deleted: bool = False) -> Optional[T]:
        """Retrieve a given model given its primary key"""
        pk_column = cast(ColumnElement, getattr(self.model, self.model.pk))

        statement = self.query(include_deleted).where(pk_column == pk).limit(1)

        return self.session.scalars(statement).first()

    def find_or_raise(self, pk: Any, include_deleted: bool = False) -> T:
        """Finds the given entity or raises an exception if the entity can not be found"""
        entity = self.find(pk, include_deleted)

        if not entity:
            raise ModelNotFoundError(
                f"The model {self.model.__name__} {pk} does not exist"
            )

        return entity

    def all(self, include_deleted: bool = False) -> Sequence[T]:
        """Retrieves all records for the given model"""
        statement = self.query(include_deleted)

        return self.session.scalars(statement).all()

    def delete(self, pk: Any) -> None:
        """Deletes a given record with the given primary key"""
        if not self._supports_soft_deletion(self.model):
            raise UnsupportedModelOperationError(
                f"The model {self.model.__name__} {pk} does not support soft deletion."
            )

        # Cast here as mypy type narrowing doesn't infer the type of entity
        # correctly
        entity = cast(AbstractBaseModel, self.find(pk))

        if entity:
            entity.deleted_at = datetime.now(UTC)

    def list(
        self, limit: int = 20, offset: int = 0, include_deleted: bool = False
    ) -> Sequence[T]:
        """Returns a list of records for the given database record"""
        statement = (
            self.query(include_deleted)
            .order_by(self.model.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return self.session.scalars(statement).all()
