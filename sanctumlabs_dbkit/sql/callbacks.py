"""
Database kit sql Callbacks
"""

from typing import List, cast

from sanctumlabs_dbkit.sql.session import Session, AsyncSession
from sanctumlabs_dbkit.sql.types import CommitCallback, CommitCallbackAsync


def on_commit(current_session: Session, callback: CommitCallback) -> None:
    """Sets a commit callback to the current session"""
    commit_hooks = cast(
        List[CommitCallback], current_session.info.setdefault("on_commit_hooks", [])
    )
    commit_hooks.append(callback)


def on_commit_async(
    current_session: AsyncSession, callback: CommitCallbackAsync
) -> None:
    """Sets an async commit callback to the current session"""
    commit_hooks = cast(
        List[CommitCallbackAsync],
        current_session.info.setdefault("on_commit_hooks", []),
    )
    commit_hooks.append(callback)
