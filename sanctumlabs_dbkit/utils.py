"""
Database utilities
"""

from typing import Optional
from sanctumlabs_dbkit.protocols import User
from sanctumlabs_dbkit.sql.models import AbstractBaseModel


def set_updated_by(user: Optional[User], entity: AbstractBaseModel) -> None:
    """Sets the entity's updated_by column to the current user or None"""
    entity.updated_by = user.user_uuid if user else None
