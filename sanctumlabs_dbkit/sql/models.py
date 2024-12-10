"""
Contains base database models that can be subclassed to add functionality & attributes for database models in an app
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, synonym

from sanctumlabs_dbkit.sql.mixins import (
    AuditedMixin,
    Base,
    SoftDeletedMixin,
    TableNameMixin,
    TimestampColumnsMixin,
    UUIDPrimaryKeyMixin,
    BaseIdentityMixin
)


# pylint: disable=too-many-ancestors
class AbstractBaseModel(
    TimestampColumnsMixin, SoftDeletedMixin, AuditedMixin, TableNameMixin, Base
):
    """
    Abstract base model that can be subclassed by a database model to include all the Mixins. The primary key is set
    to be UUID, but, the subclass implements the UUID logic
    """

    __abstract__ = True

    pk: str = "uuid"


# pylint: disable=too-many-ancestors
class BaseModel(UUIDPrimaryKeyMixin, AbstractBaseModel):
    """
    Base model that subclasses the abstract base model & adds a UUID primary key mixin setting the primary key as the
    UUID. If this is not desired, use the AbstractBaseModel instead.
    """

    __abstract__ = True

class BaseOutboxEvent(Base, BaseIdentityMixin, TableNameMixin):
    """
    Base model for outbox events. Projects can choose to add additional table args (e.g. custom index) if
    needed:

    __table_args__ = (
        Index(
            ...
        ),
    )
    """
    
    __abstract__ = True
    
    uuid: Mapped[UUID] = mapped_column(unique=True, default=uuid4)
    
    created: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    destination: Mapped[str]
    event_type: Mapped[str]
    correlation_id: Mapped[str]
    partition_key: Mapped[str]
    payload: Mapped[bytes] = mapped_column(type_=LargeBinary)
    sent_time: Mapped[Optional[datetime]]
    error_message: Mapped[Optional[str]]

    # mimic AbstractBaseModel to play nicely in the base DAO class
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:  # noqa: N805
        return synonym("created")


__all__ = [
    "AbstractBaseModel",
    "AuditedMixin",
    "Base",
    "BaseModel",
    "SoftDeletedMixin",
    "TableNameMixin",
    "TimestampColumnsMixin",
    "UUIDPrimaryKeyMixin",
    "BaseOutboxEvent",
]
