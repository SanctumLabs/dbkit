"""
Contains mixins that can be included in classes to add more functionality
"""

from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.dialects.postgresql import UUID as UUIDType
import inflection

_NOT_DELETED: datetime = datetime(1970, 1, 1, 0, 0, 1, 0, timezone.utc)


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    """
    Base class for database models
    """


# pylint: disable=too-few-public-methods
class UUIDPrimaryKeyMixin:
    """
    Primary Key Mixin that sets a UUID column as a primary key with the type set to a UUID V4
    """

    uuid: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )


# pylint: disable=too-few-public-methods
class TimestampColumnsMixin:
    """
    Timestamp Column mixin that adds timestamp columns to a table
    """

    # pylint: disable=not-callable
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    # pylint: disable=not-callable
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), index=True
    )


class SoftDeletedMixin:
    """
    A class var to indicate whether to use a timestamp (1970-01-01 00:00:01+00:00) for the 'not deleted' value of the
    'deleted_at' column for the model. Subclass models can override this and set to False to use a 'null' for 'not
    deleted' instead.
    Stores a timestamp of when a record was deleted
    """

    use_timestamp_as_not_deleted = True

    @classmethod
    def not_deleted_value(cls) -> Optional[datetime]:
        """Used to indicated whether a record has been deleted by returning the date of deletion"""
        return _NOT_DELETED if cls.use_timestamp_as_not_deleted else None

    @declared_attr
    def deleted_at(self) -> Mapped[Optional[datetime]]:
        """Returns the date of the deleted record"""
        return mapped_column(DateTime(timezone=True), default=self.not_deleted_value())


class AuditedMixin:
    """
    Mixin that contains audit information regarding database records, such as who updated a record
    """

    updated_by: Mapped[Optional[str]]


class TableNameMixin:
    """
    Mixin that creates the table names of a database
    """

    @declared_attr  # type: ignore[arg-type]
    def __tablename__(self) -> str:
        """Table names are snake case plural, for example shipping_records"""
        return inflection.pluralize(inflection.underscore(self.__name__))  # type: ignore[attr-defined]
