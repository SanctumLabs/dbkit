"""
Database Kit Types
"""

from typing import Callable
from sanctumlabs_dbkit.sql.session import Session

CommitCallback = Callable[[Session], None]
