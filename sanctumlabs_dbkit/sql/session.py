"""
Session module contains implementation logic for a database session
"""

import functools
from typing import Any, Callable, TypeVar, cast

from sqlalchemy.orm import SessionTransaction, Session as BaseSession, sessionmaker

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


class Session(BaseSession):
    """
    Session that subclasses SQLAlchemy Base Session class adding more functionality around a database session
    """

    def begin(self, nested: bool = False) -> SessionTransaction:
        """Begins a session transaction"""
        return super().begin(nested=nested or self.in_transaction())

    def transaction(self, func: FuncT) -> FuncT:
        """
        A decorator to wrap a function within a transaction.

        If we are already within a transaction, a nested transaction will be started.

        Example:

        ```python
        from sanctumlabs_dbkit import SessionLocal

        session = SessionLocal()

        @session.transaction
        def create_user(payload) -> User:
            user = User(**payload)
            session.add(user)

            return user

        create_user({"first_name": "Bob"})
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with self.begin():
                return func(*args, **kwargs)

        return cast(FuncT, wrapper)


def transaction(func: FuncT) -> FuncT:
    """
    A decorator to wrap an instance method within a transaction.

    If we are already within a transaction, a nested transaction will be started.

    Example:

    ```python
    from sanctumlabs_dbkit import SessionLocal
    from sanctumlabs_dbkit.session import transaction

    class UserService():
        def __init__(session: Session):
            self.session = session

        @transaction
        def create(payload) -> User:
            user = User(**payload)
            self.session.add(user)

            return user

    session = SessionLocal()

    user_service = UserService(session)
    user_service.create({"first_name": "Bob"})
    """

    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not self.session or not isinstance(self.session, Session):
            # pylint: disable=broad-exception-raised
            raise Exception(
                "The @transaction decorator requires that an instance variable `session` be set to an instance of a "
                "`Session`."
            )

        with self.session.begin():
            return func(self, *args, **kwargs)

    return cast(FuncT, wrapper)


SessionLocal = sessionmaker(class_=Session)
