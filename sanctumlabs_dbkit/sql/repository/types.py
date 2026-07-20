from typing import (
    TypeVar,
    Union,
)

from sanctumlabs_dbkit.sql.models import AbstractBaseModel, BaseOutboxEvent

RepositoryBaseModel = Union[AbstractBaseModel, BaseOutboxEvent]

T = TypeVar("T", bound=RepositoryBaseModel)
