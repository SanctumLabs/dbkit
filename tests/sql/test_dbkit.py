from typing import Optional
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from sqlalchemy import inspect

from tests.sql import AdminUser, User
from dbkit.sql import CommitCallback, on_commit
from dbkit.sql.repository import Repository
from dbkit.sql.session import Session, transaction


def test_hooks_are_processed_when_a_transaction_is_committed(
    database_session: Session,
) -> None:
    hook1 = MagicMock()
    hook2 = MagicMock()

    on_commit(database_session, hook1)
    on_commit(database_session, hook2)

    hook1.assert_not_called()
    hook2.assert_not_called()

    user = User(
        first_name="Bob",
        last_name="Saget",
        email="bab@saget.com",
    )
    database_session.add(user)

    hook1.assert_not_called()
    hook2.assert_not_called()

    database_session.commit()

    hook1.assert_called_once_with(database_session)
    hook2.assert_called_once_with(database_session)

    hook1.reset_mock()
    hook2.reset_mock()

    hook3 = MagicMock()
    on_commit(database_session, hook3)

    user.first_name = "Stephen"

    database_session.commit()

    hook1.assert_not_called()
    hook2.assert_not_called()
    hook3.assert_called_once_with(database_session)


def test_updated_by_user_is_set_before_session_is_flushed(
    database_session: Session,
) -> None:
    user_dao = Repository(model=User, session=database_session)

    user = user_dao.find("45a09352-4af5-4e46-a20e-29640cfd73dd")

    assert isinstance(user, User)
    assert user.updated_by is None

    setattr(
        database_session,
        "auth",
        AdminUser(user_uuid="6def1112-9812-40f4-8aba-4a1b0ea63ce1"),
    )

    user.is_admin = False

    assert user.updated_by is None

    database_session.commit()

    assert user.updated_by == "6def1112-9812-40f4-8aba-4a1b0ea63ce1"


def test_nested_database_transaction_commits_after_outer_most_context_manager(
    database_session: Session,
) -> None:
    user1 = User(
        uuid=UUID("91cb328e-7152-476c-9496-a63c87014d52"),
        first_name="Bob",
        last_name="Saget",
        email="foo@example.org",
    )

    user2 = User(
        uuid=UUID("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1"),
        first_name="John",
        last_name="Doe",
        email="john@doe.com",
    )

    hook1 = MagicMock()
    hook2 = MagicMock()

    on_commit(database_session, hook1)
    on_commit(database_session, hook2)

    with database_session.begin():
        database_session.add(user1)

        with database_session.begin():
            database_session.add(user2)

        hook1.assert_not_called()
        hook2.assert_not_called()

    assert not database_session.in_transaction()

    hook1.assert_called_once_with(database_session)
    hook2.assert_called_once_with(database_session)

    user_dao = Repository(model=User, session=database_session)

    user = user_dao.find("91cb328e-7152-476c-9496-a63c87014d52")
    assert inspect(user).persistent  # type: ignore[union-attr]

    user = user_dao.find("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1")
    assert inspect(user).persistent  # type: ignore[union-attr]


def test_nested_database_transaction_does_not_commit_if_nested_transaction_fails(
    database_session: Session,
) -> None:
    user1 = User(
        uuid=UUID("91cb328e-7152-476c-9496-a63c87014d52"),
        first_name="Bob",
        last_name="Saget",
        email="foo@example.org",
    )

    user2 = User(
        uuid=UUID("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1"),
        first_name="John",
        last_name="Doe",
        email="john@doe.com",
    )

    hook1 = MagicMock()
    hook2 = MagicMock()

    on_commit(database_session, hook1)
    on_commit(database_session, hook2)

    with pytest.raises(Exception, match="The world is ending!"):
        with database_session.begin():
            database_session.add(user1)

            with database_session.begin():
                database_session.add(user2)

            raise Exception("The world is ending!")

    assert not database_session.in_transaction()

    hook1.assert_not_called()
    hook2.assert_not_called()

    user_dao = Repository(model=User, session=database_session)

    user = user_dao.find("91cb328e-7152-476c-9496-a63c87014d52")
    assert user is None

    user = user_dao.find("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1")
    assert user is None


def test_begin_automatically_starts_a_nested_transaction_if_within_a_transaction(
    database_session: Session,
) -> None:
    user1 = User(
        uuid=UUID("91cb328e-7152-476c-9496-a63c87014d52"),
        first_name="Bob",
        last_name="Saget",
        email="foo@example.org",
    )

    user2 = User(
        uuid=UUID("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1"),
        first_name="John",
        last_name="Doe",
        email="john@doe.com",
    )

    hook1 = MagicMock()
    hook2 = MagicMock()

    on_commit(database_session, hook1)
    on_commit(database_session, hook2)

    with database_session.begin():
        database_session.add(user1)

        with database_session.begin():
            database_session.add(user2)

        hook1.assert_not_called()
        hook2.assert_not_called()

    assert not database_session.in_transaction()

    hook1.assert_called_once_with(database_session)
    hook2.assert_called_once_with(database_session)

    user_dao = Repository(model=User, session=database_session)

    user = user_dao.find("91cb328e-7152-476c-9496-a63c87014d52")
    assert inspect(user).persistent  # type: ignore[union-attr]

    user = user_dao.find("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1")
    assert inspect(user).persistent  # type: ignore[union-attr]


def test_transaction_decorator_pattern1(database_session: Session) -> None:
    user1 = User(
        uuid=UUID("91cb328e-7152-476c-9496-a63c87014d52"),
        first_name="Bob",
        last_name="Saget",
        email="foo@example.org",
    )

    user2 = User(
        uuid=UUID("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1"),
        first_name="John",
        last_name="Doe",
        email="john@doe.com",
    )

    hook1 = MagicMock()
    hook2 = MagicMock()

    on_commit(database_session, hook1)
    on_commit(database_session, hook2)

    @database_session.transaction
    def create_user1() -> None:
        database_session.add(user1)

    @database_session.transaction
    def create_user2() -> None:
        database_session.add(user2)

    @database_session.transaction
    def my_app() -> None:
        create_user1()
        create_user2()

        hook1.assert_not_called()
        hook2.assert_not_called()

    my_app()

    assert not database_session.in_transaction()

    hook1.assert_called_once_with(database_session)
    hook2.assert_called_once_with(database_session)

    user_dao = Repository(model=User, session=database_session)

    user = user_dao.find("91cb328e-7152-476c-9496-a63c87014d52")
    assert inspect(user).persistent  # type: ignore[union-attr]

    user = user_dao.find("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1")
    assert inspect(user).persistent  # type: ignore[union-attr]


def test_transaction_decorator_pattern2(database_session: Session) -> None:
    user1 = User(
        uuid=UUID("91cb328e-7152-476c-9496-a63c87014d52"),
        first_name="Bob",
        last_name="Saget",
        email="foo@example.org",
    )

    user2 = User(
        uuid=UUID("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1"),
        first_name="John",
        last_name="Doe",
        email="john@doe.com",
    )

    hook1 = MagicMock()
    hook2 = MagicMock()

    class UserService:
        def __init__(self, session: Session):
            self.session = session

        @transaction
        def create(self, user: User, hook: Optional[CommitCallback] = None) -> None:
            self.session.add(user)

            if hook:
                on_commit(self.session, hook)

    user_service = UserService(session=database_session)

    with database_session.begin():
        user_service.create(user1, hook1)
        hook1.assert_not_called()

        user_service.create(user2, hook2)
        hook2.assert_not_called()

    assert not database_session.in_transaction()

    hook1.assert_called_once_with(database_session)
    hook2.assert_called_once_with(database_session)

    user_dao = Repository(model=User, session=database_session)

    user = user_dao.find("91cb328e-7152-476c-9496-a63c87014d52")
    assert inspect(user).persistent  # type: ignore[union-attr]

    user = user_dao.find("82f9e42d-ee3c-46f7-b57c-d5fb7719bca1")
    assert inspect(user).persistent  # type: ignore[union-attr]
