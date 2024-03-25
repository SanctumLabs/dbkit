from dataclasses import dataclass
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from sanctumlabs_dbkit.sql import log_sql_statements
from sanctumlabs_dbkit.sql.models import BaseModel

log_sql_statements()


class User(BaseModel):
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    is_admin: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (UniqueConstraint("email", "deleted_at"),)


class Business(BaseModel):
    name: Mapped[Optional[str]]
    is_active: Mapped[bool] = mapped_column(default=True)


# Example of a model that overrides the 'not deleted' value as None (null)
class Card(BaseModel):
    use_timestamp_as_not_deleted = False

    number: Mapped[str]
    name: Mapped[Optional[str]]


@dataclass
class AdminUser:
    user_uuid: str
