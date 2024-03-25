"""
Database kit sql Callbacks
"""

from typing import List, cast

from sanctumlabs_dbkit.sql.session import Session
from sanctumlabs_dbkit.sql.types import CommitCallback


def on_commit(current_session: Session, callback: CommitCallback) -> None:
    """Sets a commit callback to the current session"""
    commit_hooks = cast(
        List[CommitCallback], current_session.info.setdefault("on_commit_hooks", [])
    )
    commit_hooks.append(callback)
