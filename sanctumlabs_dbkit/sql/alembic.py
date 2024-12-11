"""
Alembic utilities
"""

from typing import Any, Literal, Union

from sanctumlabs_dbkit.sql.types import PydanticModel, PydanticModelList


# pylint: disable=unused-argument
def render_item(
    type_: str, obj: Any, autogen_context: Any
) -> Union[str, Literal[False]]:
    """
    A custom renderer for the `alembic` migration framework which caters for our custom SQLAlchemy pydantic types.

    These types allow for pydantic models to be serialized and deserialized to/from json. Alembic doesn't generate the
    correct migrations for these cases so we need to do some hackery and override here.

    To leverage the custom renderer, you need to configure it on your migration context in your alembic `env.py`

    ``python
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=False,
            render_item=render_item,
        )
    ```

    See https://alembic.sqlalchemy.org/en/latest/autogenerate.html#affecting-the-rendering-of-types-themselves
    See https://gist.github.com/imankulov/4051b7805ad737ace7d8de3d3f934d6b
    """

    if type_ == "type" and isinstance(obj, (PydanticModelList, PydanticModel)):
        return "sa.JSON()"

    return False
