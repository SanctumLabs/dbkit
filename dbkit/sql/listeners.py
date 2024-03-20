from typing import List, Optional, cast
from sqlalchemy import Sequence, event
from sqlalchemy.orm import SessionTransaction, UOWTransaction, sessionmaker

from dbkit.sql.session import Session
from dbkit.sql.models import BaseModel
from dbkit.protocols import User
from dbkit.utils import set_updated_by
from dbkit.sql.types import CommitCallback

SessionLocal = sessionmaker(class_=Session)


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


@event.listens_for(SessionLocal, "after_transaction_end")
def remove_remaining_hooks(current_session: Session, transaction: SessionTransaction) -> None:
    """
    The `after_transaction_end` event triggers when a transaction ends, irrespective of whether it committed
    successfully or ended in a rollback. When this happens, and we're not in a nested transaction, we
    reset all `on_commit_hooks`.
    """
    if not transaction.parent:
        current_session.info.pop("on_commit_hooks", None)


@event.listens_for(SessionLocal, "before_flush")
def before_flush(current_session: Session, flush_context: UOWTransaction, instances: Optional[Sequence]) -> None:
    """Hook that sets the updated_by field for entities before flushing the changes with the current session"""
    if hasattr(current_session, "auth"):
        user = cast(User, current_session.auth)

        for entities in [current_session.new, current_session.dirty]:
            for entity in entities:
                if isinstance(entity, BaseModel):
                    set_updated_by(user, entity)
