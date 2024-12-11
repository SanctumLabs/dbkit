"""
Database Kit Types
"""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    SupportsIndex,
    Type,
    TypeVar,
    Union,
    cast,
)

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import Dialect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import Mutable, MutableList
from sqlalchemy.sql.type_api import TypeEngine
from wrapt import ObjectProxy

from sanctumlabs_dbkit.sql.session import Session

CommitCallback = Callable[[Session], None]

_T = TypeVar("_T", bound=BaseModel)


class SerializationOptions(BaseModel):
    """
    `SerializationOptions` are used when serialization a pydantic model to JSON.

    Example:
    ```python
    data: Mapped[SettingsData] = mapped_column(
        MutablePydanticModel.as_mutable(
            SettingsData,
            serialization_options=SerializationOptions(exclude_defaults=True),
            default=lambda: SettingsData(),
        )
    )
    ```

    Given the above example, when the settings data is serialized and persisted in the database, it will not dump
    the default model values.
    """

    exclude_defaults: bool = False


# pylint: disable=abstract-method,too-many-ancestors
class ColumnUsesPydanticModelsMixin(sa.types.TypeDecorator, TypeEngine[_T]):
    """
    ColumnUsesPydanticModelsMixin is a mixin class for serializing and deserializing pydantic models to/from
    SQLAlchemy columns.

    See https://docs.sqlalchemy.org/en/20/core/custom_types.html#marshal-json-strings
    """

    impl = sa.types.JSON

    def __init__(
        self, model: _T, serialization_options: Optional[SerializationOptions] = None
    ):
        self.model = model
        self.serialization_options = serialization_options or SerializationOptions()

        super().__init__()

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        # Use JSONB for PostgreSQL and JSON for other databases.
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB(none_as_null=True))  # type: ignore
        return dialect.type_descriptor(sa.JSON(none_as_null=True))

    def _model_to_dict(self, value: _T) -> Dict[str, Any]:
        return value.model_dump(
            exclude_defaults=self.serialization_options.exclude_defaults
        )


# pylint: disable=abstract-method, too-many-ancestors
class PydanticModel(ColumnUsesPydanticModelsMixin):
    """
    A custom SQLAlchemy column type for declaring a field as a pydantic model.

    It's important to note that changes on the pydantic model won't trigger an attribute change on the SQLAlchemy
    model. If you want mutations to be recognised, you'll need to use the `MutablePydanticModel`.

    `cart_summary: Mapped[CartSummary] = mapped_column(PydanticModel(CartSummary), default=lambda: CartSummary())`
    """

    def process_bind_param(
        self, value: Optional[BaseModel], dialect: Dialect
    ) -> Optional[Dict[str, Any]]:
        return self._model_to_dict(value) if value else None

    def process_result_value(
        self, value: Optional[Any], dialect: Dialect
    ) -> Optional[BaseModel]:
        return (
            cast(BaseModel, self.model.model_validate(value))
            if value is not None
            else None
        )

    def __repr__(self) -> str:
        return f"PydanticModel{self.model.__name__}"


# pylint: disable=abstract-method,too-few-public-methods
class PydanticModelProxy(ObjectProxy):  # type: ignore[misc]
    """
    A proxy class wrapping a pydantic model.

    The proxy class is used by the `MutablePydanticModel` and `MutablePydanticModelList` to detect changes in
    the underlying model(s). We hijack all attribute setting and trigger a change on the mutable class. As of writing,
    there is no other way to detect a change in the model.
    """

    def __init__(self, wrapped: BaseModel, mutable: Mutable):
        super().__init__(wrapped)

        self._self_mutable = mutable

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

        if name in self.__wrapped__.model_fields:
            self._self_mutable.changed()


class MutablePydanticModel(Mutable):
    """
    A custom SQLAlchemy column type for declaring a field as a pydantic model.

    Any change to the underlying pydantic model will trigger a change to the SQLAlchemy model triggering an update.

    See https://docs.sqlalchemy.org/en/14/orm/extensions/mutable.html for further docs on mutation tracking.

    `cart_summary: Mapped[CartSummary] = mapped_column(
        MutablePydanticModel.as_mutable(CartSummary), default=lambda: CartSummary()
    )`
    """

    def __init__(self, model_instance: BaseModel):
        self.proxied_model_instance = _create_proxied_pydantic_model(
            model_instance, self
        )

    @classmethod
    def as_mutable(
        cls, sqltype: Union[TypeEngine[_T], _T], **kwargs: Any
    ) -> TypeEngine[_T]:
        serialization_options = kwargs.get("serialization_options")

        return super().as_mutable(
            PydanticModel(sqltype, serialization_options=serialization_options)
        )

    @classmethod
    def coerce(cls, key: str, value: Any) -> Optional[Any]:
        if not isinstance(value, cls):
            if isinstance(value, BaseModel):
                return cls(value)

            return Mutable.coerce(key, value)
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "proxied_model_instance":
            super().__setattr__(name, value)
        else:
            setattr(self.proxied_model_instance, name, value)

    def __getattr__(self, name: str) -> Any:
        if name == "proxied_model_instance":
            # pylint: disable=no-member
            return super().__getattr__(name)  # type: ignore
        return getattr(self.proxied_model_instance, name)


class PydanticModelList(ColumnUsesPydanticModelsMixin):
    """
    A custom SQLAlchemy column type for declaring a field as a list of pydantic models.

    `products: Mapped[List[Product]] = mapped_column(PydanticModelList(Product))`
    """

    def process_bind_param(
        self, value: Optional[List[BaseModel]], dialect: Dialect
    ) -> Optional[List[Dict[str, Any]]]:
        if value:
            return [self._model_to_dict(model_instance) for model_instance in value]
        return None

    def process_result_value(
        self, value: Optional[Any], dialect: Dialect
    ) -> Optional[List[BaseModel]]:
        if value:
            return [self.model.model_validate(model_data) for model_data in value]
        return None


class MutablePydanticModelList(MutableList):
    """
    A custom SQLAlchemy column type for declaring a field as a list of pydantic models.

    Any change to the underlying pydantic models will trigger a change to the SQLAlchemy model triggering an update.

    See https://docs.sqlalchemy.org/en/14/orm/extensions/mutable.html for further docs on mutation tracking.

    `products: Mapped[List[Product]] = mapped_column(MutablePydanticModelList.as_mutable(Product))`
    """

    def __init__(self, values: Optional[Iterable[_T]] = None):
        values = values or []

        proxied_model_instances = [
            _create_proxied_pydantic_model(model_instance, self)
            for model_instance in values
        ]

        super().__init__(proxied_model_instances)

    @classmethod
    def as_mutable(
        cls, sqltype: Union[TypeEngine[_T], _T], **kwargs: Any
    ) -> TypeEngine[_T]:
        serialization_options = kwargs.get("serialization_options")

        return super().as_mutable(
            PydanticModelList(sqltype, serialization_options=serialization_options)
        )

    def __setitem__(
        self, index: SupportsIndex | slice, value: _T | Iterable[_T]
    ) -> None:
        if isinstance(value, Iterable):
            proxied_model_instances = [
                _create_proxied_pydantic_model(v, self) for v in value
            ]

            super().__setitem__(index, proxied_model_instances)
        else:
            super().__setitem__(index, _create_proxied_pydantic_model(value, self))

    def append(self, x: _T) -> None:
        super().append(_create_proxied_pydantic_model(x, self))

    def extend(self, x: Iterable[_T]) -> None:
        proxied_model_instances = [_create_proxied_pydantic_model(v, self) for v in x]

        super().extend(proxied_model_instances)

    def insert(self, i: SupportsIndex, x: _T) -> None:
        super().insert(i, _create_proxied_pydantic_model(x, self))


def _create_proxied_pydantic_model(
    model_instance: _T, mutable: Mutable
) -> PydanticModelProxy:
    if isinstance(model_instance, PydanticModelProxy):
        return model_instance
    if isinstance(model_instance, BaseModel):
        return PydanticModelProxy(model_instance, mutable)
    # pylint: disable=broad-exception-raised
    raise Exception("The model instance must be a pydantic model")


def normalise_mutable_pydantic_model(v: Any) -> Any:
    """
    A hook to automatically unwrap a `MutablePydanticModel` to its respective pydantic model.

    Example usage:

    ```python


    BusinessSocialAccountsType = Annotated[
        BusinessSocialAccounts,
        BeforeValidator(normalise_mutable_pydantic_model),
    ]

    class BusinessEntity(BaseModel):
        social_accounts: BusinessSocialAccountsType = Field(
            default_factory=BusinessSocialAccounts
        )
    ```

    In this example, if we were to store the `BusinessSocialAccounts` in a database column, it would be wrapped
    within mutable and proxy objects.  If we were to later try and construct a `BusinessEntity` using
    `model_validate()`, it would complain that we're
    trying to set a field expecting type `BusinessSocialAccounts` to something which is a `MutablePydanticModel`.
    We therefore use the hook to normalise the proxy model to the actual pydantic model.
    """

    if isinstance(v, MutablePydanticModel):
        return v.proxied_model_instance.__wrapped__

    return v


def default_to_pydantic_model(model: Type[BaseModel]) -> Callable[[Any], Any]:
    """
    A hook to automatically set a field to an instance of a pydantic model if constructing without a value.

    Example usage:

    ```python
    BusinessSocialAccountsType = Annotated[
        BusinessSocialAccounts,
        BeforeValidator(default_to_pydantic_model(BusinessSocialAccounts)),
    ]

    class BusinessEntity(BaseModel):
        social_accounts: BusinessSocialAccountsType = Field(
            default_factory=BusinessSocialAccounts
        )
    ```
    """

    def _validator(v: Any) -> Any:
        return model() if not v else v

    return _validator
