from sqlalchemy_utils import force_instant_defaults

from dbkit.sql.session import Session, SessionLocal
from dbkit.sql.listeners import process_hooks, remove_remaining_hooks, before_flush
from dbkit.sql.logger import log_sql_statements
from dbkit.sql.types import CommitCallback
from dbkit.sql.callbacks import on_commit

# sets defaults for columns in the models on instantiation
force_instant_defaults()

__all__ = [
    "process_hooks",
    "remove_remaining_hooks",
    "before_flush",
    "log_sql_statements",
    "on_commit",
    "SessionLocal"
]
