"""
Protocols defining types
"""

from typing import Protocol


# pylint: disable=too-few-public-methods
class User(Protocol):
    """Defines a User protocol, classes that have a similar signature can be used to define a user 'entity'. Note that
    this is not the same as a User database model. This can be used to extract information from a request for example
    """

    @property
    def user_uuid(self) -> str:
        """Retrieve the user UUID"""
        return ""
