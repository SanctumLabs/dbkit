"""
Contains base database models that can be subclassed to add functionality & attributes for database models in an app
"""

from dbkit.sql.mixins import (
    AuditedMixin,
    Base,
    SoftDeletedMixin,
    TableNameMixin,
    TimestampColumnsMixin,
    UUIDPrimaryKeyMixin,
)


class AbstractBaseModel(
    TimestampColumnsMixin, SoftDeletedMixin, AuditedMixin, TableNameMixin, Base
):
    """
    Abstract base model that can be subclassed by a database model to include all the Mixins. The primary key is set
    to be UUID, but, the subclass implements the UUID logic
    """

    __abstract__ = True

    pk: str = "uuid"


class BaseModel(UUIDPrimaryKeyMixin, AbstractBaseModel):
    """
    Base model that subclasses the abstract base model & adds a UUID primary key mixin setting the primary key as the
    UUID. If this is not desired, use the AbstractBaseModel instead.
    """

    __abstract__ = True


__all__ = [
    "AbstractBaseModel",
    "AuditedMixin",
    "Base",
    "BaseModel",
    "SoftDeletedMixin",
    "TableNameMixin",
    "TimestampColumnsMixin",
    "UUIDPrimaryKeyMixin",
]