"""
Database Kit Types
"""
from typing import Callable
from dbkit.sql.session import Session

CommitCallback = Callable[[Session], None]
