from dataclasses import dataclass
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped

from sanctumlabs_dbkit.exceptions import ModelNotFoundError
from sanctumlabs_dbkit.sql import SessionLocal, log_sql_statements, on_commit
from sanctumlabs_dbkit.sql.repository import Repository
from sanctumlabs_dbkit.sql.mixins import Base
from sanctumlabs_dbkit.sql.models import BaseModel
from sanctumlabs_dbkit.sql.session import Session
from sanctumlabs_dbkit.sql.utils import get_changes, has_any_changed, has_changed

# Logging raw SQL statements

log_sql_statements()


# Defining a model
class Address(BaseModel):
    line1: Mapped[str]
    line2: Mapped[Optional[str]]
    suburb: Mapped[str]


# Creating a database session

database_url = (
    "postgresql://sanctumlabs:sanctumlabs@localhost:5437/sanctumlabs_dbkit-sql"
)

engine = create_engine(database_url)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

SessionLocal.configure(bind=engine)

session = SessionLocal()

# Defining a Repository

address_dao = Repository(model=Address, session=session)

# Creating a model

address = Address(line1="21", line2="Jump Street", suburb="FooBar")
session.add(address)

# Explicitly committing a transaction

session.commit()

# Implicitly committing a transaction

with session.begin():
    address = Address(line1="21", line2="Jump Street", suburb="FooBar")
    session.add(address)


# Using a transaction decorator to implicitly commit


@session.transaction
def foo() -> None:
    address = Address(line1="21", line2="Jump Street", suburb="FooBar")
    session.add(address)


# Adding a hook that runs when a transaction is committed


def on_commit_callback(session: Session) -> None:
    print("The transaction was committed.")
    print(
        "This would be a good time to do things like sending emails and enqueueing tasks."
    )


on_commit(session, on_commit_callback)

address.line1 = "22"
session.commit()

# Retrieving a model by pk

my_address = address_dao.find("2c8081f3-af23-466c-a136-cfd1d6e4dccc")

# Retrieving all models

addresses = address_dao.all()

# Deleting a model

address_dao.delete(address.uuid)

# Retrieving a model by pk or raising an exception

try:
    address_dao.find_or_raise("2c8081f3-af23-466c-a136-cfd1d6e4dccc")
except ModelNotFoundError:
    print("Oh no, the model does not exist!")

# Checking for changes in a model's state

new_address = Address(line1="21", line2="Jump Street", suburb="FooBar")
session.add(new_address)
session.commit()
session.refresh(new_address)

print(get_changes(new_address))
# {}

new_address.line1 = "22"

print(get_changes(new_address))
# {'line1': ('21', '22')}

new_address.line2 = "Blah"

print(get_changes(new_address))
# {'line1': ('21', '22'), 'line2': ('Jump Street', 'Blah')}

print(has_changed(new_address, "line1"))
# True

print(has_changed(new_address, "line2"))
# True

print(has_changed(new_address, "suburb"))
# False

print(has_any_changed(new_address, ["line1", "suburb"]))


# True

# Tracking who changed a model


@dataclass
class AdminUser:
    user_uuid: str


setattr(session, "auth", AdminUser(user_uuid="685f423f-2cb1-48d1-a36b-c78fe28f9a14"))

assert new_address.updated_by is None
session.commit()
assert new_address.updated_by == "685f423f-2cb1-48d1-a36b-c78fe28f9a14"


# Defining a model that overrides the 'not deleted' value and uses null instead of a timestamp
class CardReader(BaseModel):
    use_timestamp_as_not_deleted = False

    serial_number: Mapped[str]
    name: Mapped[Optional[str]]
