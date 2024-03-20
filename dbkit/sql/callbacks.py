from typing import List, cast

from dbkit.sql.session import Session
from dbkit.sql.types import CommitCallback


def on_commit(current_session: Session, callback: CommitCallback) -> None:
    """Sets a commit callback to the current session"""
    commit_hooks = cast(List[CommitCallback], current_session.info.setdefault("on_commit_hooks", []))
    commit_hooks.append(callback)
