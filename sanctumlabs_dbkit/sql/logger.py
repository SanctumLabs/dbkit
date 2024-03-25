"""
Logger configuration
"""

import logging

logger = logging.getLogger(__name__)


def log_sql_statements() -> None:
    """Sets the logging level to INFO for the sqlalchemy engine"""
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
