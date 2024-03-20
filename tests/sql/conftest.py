import os
from datetime import datetime, UTC
from typing import Any, Generator
from uuid import UUID

import pytest
from sqlalchemy import create_engine

from tests.sql import Business, Card, User
from dbkit.sql import SessionLocal
from dbkit.sql.models import Base
from dbkit.sql.session import Session


@pytest.fixture
def database_session() -> Generator[Session, Any, None]:
    database_url = os.environ.get(
        "DATABASE_URL", "postgresql://sanctumlabs:sanctumlabs@localhost:5432/dbkit-sql"
    )

    engine = create_engine(database_url)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal.configure(bind=engine)

    session = SessionLocal()

    try:
        session.add_all(
            [
                User(
                    uuid=UUID("45a09352-4af5-4e46-a20e-29640cfd73dd"),
                    first_name="John",
                    last_name="Doe",
                    email="j.doe@sanctumlabs.com",
                ),
                User(
                    first_name="Jane",
                    last_name="Doe",
                    email="jane.doe@sanctumlabs.com",
                    is_admin=True,
                ),
                User(
                    uuid=UUID("9c809286-9aa8-4863-bb03-645c3bc065ce"),
                    first_name="Mr",
                    last_name="Robot",
                    email="mr.robot@sanctumlabs.com",
                    deleted_at=datetime.now(UTC),
                ),
                Business(name="SanctumLabs"),
                Business(name="RusticW olf", is_active=False),
                Card(
                    uuid=UUID("f0bbf5dd-0b9e-45a3-8bbf-412cd7fadf89"),
                    number="12345",
                ),
                Card(
                    uuid=UUID("89fbad38-aedb-491a-a579-ed0a69a9e7d6"),
                    number="67890",
                    deleted_at=datetime.now(UTC),
                ),
            ]
        )
        session.commit()

        yield session
    finally:
        session.close()

    Base.metadata.drop_all(bind=engine)
