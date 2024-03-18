import logging
from typing import Callable, List, Optional, Protocol, cast

from sqlalchemy import Sequence, event
from sqlalchemy.orm import SessionTransaction, UOWTransaction, sessionmaker
from sqlalchemy_utils import force_instant_defaults

from dbkit.models import AbstractBaseModel, BaseModel
from dbkit.session import Session

logger = logging.getLogger(__name__)

# sets defaults for columns in the models on instantiation
force_instant_defaults()

CommitCallback = Callable[[Session], None]

SessionLocal = sessionmaker(class_=Session)


class User(Protocol):
    """Defines a User protocol, classes that have a similar signature can be used to define a user 'entity'. Note that
    this is not the same as a User database model. This can be used to extract information from a request for example"""

    @property
    def user_uuid(self) -> str:
        """Retrieve the user UUID"""
        return ""


def log_sql_statements() -> None:
    """Sets the logging level to INFO for the sqlalchemy engine """
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


@event.listens_for(SessionLocal, "after_commit")
def process_hooks(current_session: Session) -> None:
    """The `after_commit` event triggers when any transaction, root or nested, is committed. We therefore first check
    if we're in the outermost transaction and only trigger the commit callbacks if so.
    """
    if not current_session.in_nested_transaction():
        hooks = cast(List[CommitCallback], current_session.info.get("on_commit_hooks", []))

        while hooks:
            fn = hooks.pop(0)
            fn(current_session)
