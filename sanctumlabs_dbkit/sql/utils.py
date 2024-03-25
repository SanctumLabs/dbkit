"""
Database Kit SQL Utilities
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import inspect
from sqlalchemy.orm import InstanceState, PassiveFlag

from sanctumlabs_dbkit.sql.models import AbstractBaseModel


def get_changes(entity: AbstractBaseModel) -> Dict[str, Tuple[Any, Any]]:
    """
    Return a dictionary containing changes made to the model since it was
    fetched from the database. In the case of a nested transaction, only changes from the most recent savepoint
    will reflect.

    The dictionary is of the form {'property_name': [old_value, new_value]}

    Example:
      user = get_user_by_id(420)
      >>> '<User id=402 email="business_email@gmail.com">'
      get_model_changes(user)
      >>> {}
      user.email = 'new_email@who-dis.biz'
      get_model_changes(user)
      >>> {'email': ['business_email@gmail.com', 'new_email@who-dis.biz']}
    """
    state: InstanceState = inspect(entity)

    changes: Dict[str, Tuple[Any, Any]] = {}

    for attr in state.attrs:
        hist = state.get_history(attr.key, PassiveFlag.PASSIVE_OFF)

        if not hist.has_changes():
            continue

        old_value = hist.deleted[0] if hist.deleted else None
        new_value = hist.added[0] if hist.added else None
        changes[attr.key] = (old_value, new_value)

    return changes


def has_changed(entity: AbstractBaseModel, key: Optional[str] = None) -> bool:
    """
    Returns a boolean indicating if the attribute `key` on `entity` has changed since it was
    fetched from the database. In the case of a nested transaction, only changes from the most recent savepoint
    will reflect.
    """
    return has_any_changed(entity, [key]) if key else len(get_changes(entity)) > 0


def has_any_changed(entity: AbstractBaseModel, keys: List[str]) -> bool:
    """
    Returns a boolean indicating if any attributes on `entity` have changed since it was
    fetched from the database. In the case of a nested transaction, only changes from the most recent savepoint
    will reflect.
    """
    changes = get_changes(entity)
    changed_keys = changes.keys()

    intersected_keys = list(set(changed_keys) & set(keys))

    return len(intersected_keys) > 0
