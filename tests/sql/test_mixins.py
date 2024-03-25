from datetime import datetime, timezone

from tests.sql import Card, User
from sanctumlabs_dbkit.sql.repository import Repository
from sanctumlabs_dbkit.sql.session import Session


def test_soft_deleted_mixin_subclasses_can_override_deleted_at(
    database_session: Session,
) -> None:
    card_reader_repo = Repository(model=Card, session=database_session)

    card_reader = card_reader_repo.find("f0bbf5dd-0b9e-45a3-8bbf-412cd7fadf89")

    assert isinstance(card_reader, Card)
    assert card_reader.deleted_at is None


def test_soft_deleted_mixin_defaults_to_timestamp_deleted_at(
    database_session: Session,
) -> None:
    user_repo = Repository(model=User, session=database_session)

    user = user_repo.find_or_raise("45a09352-4af5-4e46-a20e-29640cfd73dd")

    assert user.deleted_at == datetime(1970, 1, 1, 0, 0, 1, 0, timezone.utc)
