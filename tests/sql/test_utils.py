from tests.sql import User
from dbkit.sql.repository import Repository
from dbkit.sql.session import Session
from dbkit.sql.utils import get_changes, has_any_changed, has_changed


def test_get_changes(database_session: Session) -> None:
    user_repo = Repository(model=User, session=database_session)

    user = database_session.execute(
        user_repo.query().where(User.email == "j.doe@sanctumlabs.com")
    ).scalar_one()

    assert isinstance(user, User)

    assert get_changes(user) == {}

    user.first_name = "John"

    assert get_changes(user) == {}

    user.first_name = "Bob"

    assert get_changes(user) == {"first_name": ("John", "Bob")}

    user.email = "foobar@sanctumlabs.com"

    assert get_changes(user) == {
        "first_name": ("John", "Bob"),
        "email": ("j.doe@sanctumlabs.com", "foobar@sanctumlabs.com"),
    }

    database_session.commit()

    assert get_changes(user) == {}


def test_has_changed(database_session: Session) -> None:
    user_repo = Repository(model=User, session=database_session)

    with database_session.begin():
        user = database_session.execute(
            user_repo.query().where(User.email == "j.doe@sanctumlabs.com")
        ).scalar_one()

        assert isinstance(user, User)
        assert not has_changed(user, "first_name")

        user.first_name = "John"
        assert not has_changed(user, "first_name")

        user.first_name = "Bob"
        assert has_changed(user, "first_name")

        # Test with nested transactions. Only changes from the most recent savepoint will reflect
        with database_session.begin():
            assert not has_changed(user, "first_name")

            user.first_name = "Larry"
            assert has_changed(user, "first_name")

    assert not has_changed(user, "first_name")
    assert user.first_name == "Larry"


def test_has_any_changed(database_session: Session) -> None:
    user_repo = Repository(model=User, session=database_session)

    user = database_session.execute(
        user_repo.query().where(User.email == "j.doe@sanctumlabs.com")
    ).scalar_one()

    assert isinstance(user, User)

    assert not has_any_changed(user, ["first_name"])

    user.first_name = "John"

    assert not has_any_changed(user, ["first_name"])

    user.first_name = "Bob"

    assert has_any_changed(user, ["first_name"])

    database_session.commit()

    assert not has_any_changed(user, ["first_name"])
