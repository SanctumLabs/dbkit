"""
Async Session module contains implementation logic for a database session
"""

import functools
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession as BaseAsyncSession,
    AsyncSessionTransaction,
    async_sessionmaker,
)

from sanctumlabs_dbkit.sql.session.types import FuncT


class AsyncSession(BaseAsyncSession):
    """
    Session that subclasses SQLAlchemy Base Session class adding more functionality around a database session
    """

    def begin(self, nested: bool = False) -> AsyncSessionTransaction:
        """Begins an async session transaction"""
        if nested or self.in_transaction():
            return super().begin_nested()
        return super().begin()

    def transaction(self, func: FuncT) -> FuncT:
        """
        A decorator to wrap a function within a transaction.

        If we are already within a transaction, a nested transaction will be started.

        Example:

        ```python
        from sanctumlabs_dbkit.sql.session import AsyncSessionLocal

        session = SessionLocal()

        @session.transaction
        def create_user(payload) -> User:
            user = User(**payload)
            session.add(user)

            return user

        create_user({"first_name": "Bob"})
        """

        `@functools.wraps`(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with self.begin():
                return await func(*args, **kwargs)

        return cast(FuncT, wrapper)


async def async_transaction(func: FuncT) -> FuncT:
    """
    A decorator to wrap an instance method within a transaction.

    If we are already within a transaction, a nested transaction will be started.

    Example:

    ```python
    from sanctumlabs_dbkit.sql.session import AsyncSessionLocal
    from sanctumlabs_dbkit.sql.sesison import async_transaction

    class UserService():
        def __init__(session: AsyncSession):
            self.session = session

        @async_transaction
        def create(payload) -> User:
            user = User(**payload)
            self.session.add(user)

            return user

    session = AsyncSessionLocal()

    user_service = UserService(session)
    user_service.create({"first_name": "Bob"})
    """

    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not self.session or not isinstance(self.session, AsyncSession):
            # pylint: disable=broad-exception-raised
            raise Exception(
                "The @transaction decorator requires that an instance variable `session` be set to an instance of a "
                "`Session`."
            )

        async with self.session.begin():
            return func(self, *args, **kwargs)

    return wrapper


AsyncSessionLocal = async_sessionmaker(class_=AsyncSession)
