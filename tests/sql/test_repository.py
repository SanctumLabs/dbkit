import pytest

from tests.sql import Card, User
from sanctumlabs_dbkit.sql.repository import Repository
from sanctumlabs_dbkit.exceptions import ModelNotFoundError
from sanctumlabs_dbkit.sql.session import Session


def test_query(database_session: Session) -> None:
    user_dao = Repository(model=User, session=database_session)

    statement = user_dao.query().where(User.email == "j.doe@sanctumlabs.com")

    user = database_session.execute(statement).scalar_one()

    assert isinstance(user, User)
    assert user.email == "j.doe@sanctumlabs.com"


def test_query_returns_deleted_models_when_include_deleted_is_true(
    database_session: Session,
) -> None:
    user_dao = Repository(model=User, session=database_session)

    user1 = database_session.execute(
        user_dao.query().where(User.email == "mr.robot@sanctumlabs.com")
    ).scalar_one_or_none()

    assert user1 is None

    user2 = database_session.execute(
        user_dao.query(include_deleted=True).where(
            User.email == "mr.robot@sanctumlabs.com"
        )
    ).scalar_one()

    assert isinstance(user2, User)
    assert user2.email == "mr.robot@sanctumlabs.com"


def test_find(database_session: Session) -> None:
    user_dao = Repository(model=User, session=database_session)

    user = user_dao.find("45a09352-4af5-4e46-a20e-29640cfd73dd")

    assert isinstance(user, User)

    assert user.email == "j.doe@sanctumlabs.com"


def test_find_returns_deleted_model_when_include_deleted_is_true(
    database_session: Session,
) -> None:
    # Models with default 'not deleted' value (timestamp)
    user_dao = Repository(model=User, session=database_session)

    user1 = user_dao.find("9c809286-9aa8-4863-bb03-645c3bc065ce")

    assert user1 is None

    user2 = user_dao.find(
        "9c809286-9aa8-4863-bb03-645c3bc065ce",
        include_deleted=True,
    )

    assert isinstance(user2, User)
    assert user2.email == "mr.robot@sanctumlabs.com"

    # Models with overridden 'not deleted' value (null)
    card_reader_dao = Repository(model=Card, session=database_session)

    card_reader = card_reader_dao.find("89fbad38-aedb-491a-a579-ed0a69a9e7d6")

    assert card_reader is None

    card_reader = card_reader_dao.find(
        "89fbad38-aedb-491a-a579-ed0a69a9e7d6", include_deleted=True
    )

    assert isinstance(card_reader, Card)
    assert card_reader.number == "67890"


def test_find_or_raise(database_session: Session) -> None:
    user_dao = Repository(model=User, session=database_session)

    user = user_dao.find_or_raise("45a09352-4af5-4e46-a20e-29640cfd73dd")

    assert isinstance(user, User)

    assert user.email == "j.doe@sanctumlabs.com"


def test_find_or_raise_returns_deleted_model_when_include_deleted_is_true(
    database_session: Session,
) -> None:
    user_dao = Repository(model=User, session=database_session)

    with pytest.raises(ModelNotFoundError):
        user_dao.find_or_raise("9c809286-9aa8-4863-bb03-645c3bc065ce")

    user = user_dao.find_or_raise(
        "9c809286-9aa8-4863-bb03-645c3bc065ce",
        include_deleted=True,
    )

    assert isinstance(user, User)
    assert user.email == "mr.robot@sanctumlabs.com"


def test_find_or_raise_raises_exception_when_model_does_not_exist(
    database_session: Session,
) -> None:
    user_dao = Repository(model=User, session=database_session)

    with pytest.raises(ModelNotFoundError):
        user_dao.find_or_raise("ad228d65-c97e-4b46-b842-ae9b05be42cd")


def test_all(database_session: Session) -> None:
    user_dao = Repository(model=User, session=database_session)

    users = user_dao.all()

    assert len(users) == 2

    user1 = users[0]
    assert isinstance(user1, User)
    assert user1.email == "j.doe@sanctumlabs.com"

    user2 = users[1]
    assert isinstance(user2, User)
    assert user2.email == "jane.doe@sanctumlabs.com"


def test_all_returns_deleted_when_include_deleted_is_true(
    database_session: Session,
) -> None:
    user_dao = Repository(model=User, session=database_session)

    users = user_dao.all(include_deleted=True)

    assert len(users) == 3

    user1 = users[0]
    assert isinstance(user1, User)
    assert user1.email == "j.doe@sanctumlabs.com"

    user2 = users[1]
    assert isinstance(user2, User)
    assert user2.email == "jane.doe@sanctumlabs.com"

    user3 = users[2]
    assert isinstance(user3, User)
    assert user3.email == "mr.robot@sanctumlabs.com"


def test_delete(database_session: Session) -> None:
    user_dao = Repository(model=User, session=database_session)

    user = database_session.execute(
        user_dao.query().where(User.email == "j.doe@sanctumlabs.com")
    ).scalar_one()

    assert isinstance(user, User)
    assert user.email == "j.doe@sanctumlabs.com"
    assert user.deleted_at == User.not_deleted_value()

    user_dao.delete(user.uuid)

    user = database_session.execute(
        user_dao.query().where(User.email == "j.doe@sanctumlabs.com")
    ).scalar_one_or_none()

    assert user is None


def test_list(database_session: Session) -> None:
    user_dao = Repository(model=User, session=database_session)

    users = user_dao.list()

    assert len(users) == 2

    user1 = users[0]
    assert isinstance(user1, User)
    assert user1.email == "j.doe@sanctumlabs.com"

    user2 = users[1]
    assert isinstance(user2, User)
    assert user2.email == "jane.doe@sanctumlabs.com"


def test_list_offset(database_session: Session) -> None:
    user_dao = Repository(model=User, session=database_session)

    users = user_dao.list(offset=1)

    assert len(users) == 1

    user2 = users[0]
    assert isinstance(user2, User)
    assert user2.email == "jane.doe@sanctumlabs.com"


def test_list_limit(database_session: Session) -> None:
    user_dao = Repository(model=User, session=database_session)

    users = user_dao.list(limit=1)

    assert len(users) == 1

    user1 = users[0]
    assert isinstance(user1, User)
    assert user1.email == "j.doe@sanctumlabs.com"
