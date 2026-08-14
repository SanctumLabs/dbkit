import pytest
from datetime import timezone

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sanctumlabs_dbkit.sql.session.async_session import AsyncSession, async_transaction
from sanctumlabs_dbkit.sql.repository.async_repository import AsyncWriteRepository


@pytest.mark.asyncio
async def test_async_transaction_decorator_executes_and_awaits():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    SessionMaker = async_sessionmaker(class_=AsyncSession, bind=engine)
    async with SessionMaker() as session:
        class Dummy:
            def __init__(self, session):
                self.session = session

            @async_transaction
            async def do_work(self):
                return "done"

        dummy = Dummy(session)
        result = await dummy.do_work()
        assert result == "done"


@pytest.mark.asyncio
async def test_async_transaction_raises_when_no_session():
    class Dummy:
        def __init__(self, session):
            self.session = session

        @async_transaction
        async def do_work(self):
            return "done"

    dummy = Dummy(None)
    with pytest.raises(Exception):
        await dummy.do_work()


@pytest.mark.asyncio
async def test_async_session_transaction_decorator_accepts_function():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    SessionMaker = async_sessionmaker(class_=AsyncSession, bind=engine)
    async with SessionMaker() as session:
        @session.transaction
        async def my_task():
            return 123

        assert await my_task() == 123


@pytest.mark.asyncio
async def test_delete_sets_timezone_aware():
    # Make a fake model and repo with overridden find()
    # Use a plain fake model and force the repository to treat it as soft-deletable
    class FakeModel:
        pk = "id"
        created_at = None
        deleted_at = None

        @classmethod
        def not_deleted_value(cls):
            return None

    class DummyRepo(AsyncWriteRepository):
        async def find(self, pk, include_deleted=False):
            inst = FakeModel()
            return inst

    repo = DummyRepo(model=FakeModel, session=None)
    # Force soft-deletion support for testing
    repo._supports_soft_deletion = lambda model: True

    # Ensure delete mutates a persistent instance
    persistent = FakeModel()

    async def persistent_find(pk, include_deleted=False):
        return persistent

    repo.find = persistent_find
    await repo.delete("x")
    assert persistent.deleted_at is not None
    assert persistent.deleted_at.tzinfo == timezone.utc
