from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import JSON, text
from sqlalchemy.orm import Mapped, mapped_column

from sanctumlabs_dbkit.sql.repository import DAO
from sanctumlabs_dbkit.sql.models import BaseModel
from sanctumlabs_dbkit.sql.session import Session
from sanctumlabs_dbkit.sql.types import (
    MutablePydanticModel,
    MutablePydanticModelList,
    PydanticModel,
    SerializationOptions,
)


class Child(PydanticBaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    favourite_food: List[str]
    attributes: Dict[str, Any]


class Person(BaseModel):
    name: Mapped[str]
    children: Mapped[JSON] = mapped_column(type_=JSON)


def test_sqlalchemy_uses_pydantic_json_serializer_to_serialize_json(
    database_session: Session,
) -> None:
    with database_session.begin():
        person = Person(
            name="Pam Goslett",
            children=[
                Child(
                    first_name="Matthew",
                    last_name="Goslett",
                    date_of_birth=date(1987, 7, 31),
                    favourite_food=["ribs", "dim sum", "sushi"],
                    attributes={
                        "eye_colour": "hazel",
                        "hair_colour": "brown",
                        "star_sign": "leo",
                    },
                )
            ],
        )

        database_session.add(person)

    people_dao = DAO(Person, database_session)

    people = people_dao.all()

    assert len(people) == 1

    pam_goslett: Person = people[0]

    assert pam_goslett.name == "Pam Goslett"

    children = cast(List[Dict[str, Any]], pam_goslett.children)

    assert children == [
        {
            "first_name": "Matthew",
            "last_name": "Goslett",
            "date_of_birth": "1987-07-31",
            "favourite_food": ["ribs", "dim sum", "sushi"],
            "attributes": {
                "eye_colour": "hazel",
                "hair_colour": "brown",
                "star_sign": "leo",
            },
        }
    ]


class Product(PydanticBaseModel):
    name: str
    brand: str
    price: Decimal
    is_for_sale: bool = True


class CartSummary(PydanticBaseModel):
    gross_amount: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")


class AttributionSource(PydanticBaseModel):
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]


class Catalogue(BaseModel):
    products: Mapped[List[Product]] = mapped_column(
        MutablePydanticModelList.as_mutable(
            Product, serialization_options=SerializationOptions(exclude_defaults=True)
        ),
        nullable=True,
    )


class Cart(BaseModel):
    shipping_first_name: Mapped[str]
    products: Mapped[List[Product]] = mapped_column(
        MutablePydanticModelList.as_mutable(Product), nullable=True
    )
    cart_summary: Mapped[CartSummary] = mapped_column(
        MutablePydanticModel.as_mutable(CartSummary), default=lambda: CartSummary()
    )
    attribution_source: Mapped[Optional[AttributionSource]] = mapped_column(
        PydanticModel(AttributionSource)
    )


class SettingsData(PydanticBaseModel):
    invoice_email_address: str = "foo@bar.com"
    show_address_on_invoice: bool = True
    invoice_footer_text: Optional[str] = None


class Settings(BaseModel):
    data: Mapped[SettingsData] = mapped_column(
        MutablePydanticModel.as_mutable(
            SettingsData,
            serialization_options=SerializationOptions(exclude_defaults=True),
            default=lambda: SettingsData(),
        )
    )


def test_sqlalchemy_serializes_value_in_pydantic_model_column(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(
            shipping_first_name="Matthew",
            products=[],
            cart_summary=CartSummary(
                gross_amount=Decimal("100"),
                discount=Decimal("45"),
                net_amount=Decimal("55"),
            ),
            attribution_source=AttributionSource(
                utm_source="facebook",
                utm_medium="social",
                utm_campaign="yoco_2022_march_madness",
            ),
        )

        database_session.add(cart)

    assert cart.shipping_first_name == "Matthew"
    assert cart.cart_summary.gross_amount == Decimal("100")
    assert cart.cart_summary.discount == Decimal("45")
    assert cart.cart_summary.net_amount == Decimal("55")

    assert isinstance(cart.attribution_source, AttributionSource)
    assert cart.attribution_source.utm_source == "facebook"
    assert cart.attribution_source.utm_medium == "social"
    assert cart.attribution_source.utm_campaign == "yoco_2022_march_madness"


def test_sqlalchemy_serializes_value_in_pydantic_model_column_and_excludes_defaults_when_specified(
    database_session: Session,
) -> None:
    with database_session.begin():
        settings = Settings(data=SettingsData(show_address_on_invoice=False))

        database_session.add(settings)

    assert settings.data.invoice_email_address == "foo@bar.com"
    assert not settings.data.show_address_on_invoice
    assert settings.data.invoice_footer_text is None

    row = database_session.execute(text("SELECT * FROM settings")).first()

    assert row.data == {"show_address_on_invoice": False}  # type: ignore


def test_sqlalchemy_serializes_value_in_pydantic_model_column_and_excludes_defaults_when_specified_and_correctly_handles_case_where_value_is_default(
    database_session: Session,
) -> None:
    with database_session.begin():
        settings = Settings(data=SettingsData())

        database_session.add(settings)

    assert settings.data.model_dump() == SettingsData().model_dump()

    row = database_session.execute(text("SELECT * FROM settings")).first()

    assert row.data == {}  # type: ignore


def test_sqlalchemy_serializes_value_in_pydantic_model_column_when_value_is_null(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(
            shipping_first_name="Matthew",
            cart_summary=CartSummary(
                gross_amount=Decimal("100"),
                discount=Decimal("45"),
                net_amount=Decimal("55"),
            ),
        )

        database_session.add(cart)

    assert cart.shipping_first_name == "Matthew"
    assert cart.cart_summary.gross_amount == Decimal("100")
    assert cart.cart_summary.discount == Decimal("45")
    assert cart.cart_summary.net_amount == Decimal("55")
    assert cart.attribution_source is None


def test_sqlalchemy_serializes_value_in_pydantic_model_column_and_sets_default_value_when_not_present(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(shipping_first_name="Matthew")

        database_session.add(cart)

    assert cart.cart_summary.gross_amount == Decimal("0")
    assert cart.cart_summary.discount == Decimal("0")
    assert cart.cart_summary.net_amount == Decimal("0")


def test_sqlalchemy_updates_value_in_pydantic_model_column(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(
            shipping_first_name="Matthew",
            cart_summary=CartSummary(
                gross_amount=Decimal("100"),
                discount=Decimal("45"),
                net_amount=Decimal("55"),
            ),
            attribution_source=AttributionSource(
                utm_source="facebook",
                utm_medium="social",
                utm_campaign="yoco_2022_march_madness",
            ),
        )
        database_session.add(cart)

    assert cart.shipping_first_name == "Matthew"
    assert cart.cart_summary.gross_amount == Decimal("100")
    assert cart.cart_summary.discount == Decimal("45")
    assert cart.cart_summary.net_amount == Decimal("55")

    assert isinstance(cart.attribution_source, AttributionSource)
    assert cart.attribution_source.utm_source == "facebook"
    assert cart.attribution_source.utm_medium == "social"
    assert cart.attribution_source.utm_campaign == "yoco_2022_march_madness"

    cart.shipping_first_name = "Bob"
    cart.cart_summary.gross_amount = Decimal("45")
    cart.cart_summary.discount = Decimal("0")
    cart.cart_summary.net_amount = Decimal("45")
    cart.attribution_source.utm_source = "google"

    database_session.commit()

    assert cart.shipping_first_name == "Bob"
    assert cart.cart_summary.gross_amount == Decimal("45")
    assert cart.cart_summary.discount == Decimal("0")
    assert cart.cart_summary.net_amount == Decimal("45")
    # cart.attribution_source.utm_source should not have changed since the field isn't mutable or monitored
    assert cart.attribution_source.utm_source == "facebook"
    assert cart.attribution_source.utm_medium == "social"
    assert cart.attribution_source.utm_campaign == "yoco_2022_march_madness"


def test_sqlalchemy_serializes_value_in_pydantic_model_list_column(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(
            shipping_first_name="Matthew",
            products=[
                Product(name="Kit Kat Chunky", brand="Kit Kat", price=Decimal("2.45")),
                Product(name="Nike Pegasus 39", brand="Nike", price=Decimal("2499")),
            ],
        )

        database_session.add(cart)

    assert len(cart.products) == 2

    assert cart.products[0].name == "Kit Kat Chunky"
    assert cart.products[0].brand == "Kit Kat"
    assert cart.products[0].price == Decimal("2.45")
    assert cart.products[0].is_for_sale

    assert cart.products[1].name == "Nike Pegasus 39"
    assert cart.products[1].brand == "Nike"
    assert cart.products[1].price == Decimal("2499")
    assert cart.products[1].is_for_sale


def test_sqlalchemy_serializes_value_in_pydantic_model_list_column_and_excludes_defaults_when_specified(
    database_session: Session,
) -> None:
    with database_session.begin():
        catalogue = Catalogue(
            products=[
                Product(name="Kit Kat Chunky", brand="Kit Kat", price=Decimal("2.45")),
                Product(
                    name="Nike Pegasus 39",
                    brand="Nike",
                    price=Decimal("2499"),
                    is_for_sale=False,
                ),
            ],
        )

        database_session.add(catalogue)

    assert len(catalogue.products) == 2

    assert catalogue.products[0].name == "Kit Kat Chunky"
    assert catalogue.products[0].brand == "Kit Kat"
    assert catalogue.products[0].price == Decimal("2.45")
    assert catalogue.products[0].is_for_sale

    assert catalogue.products[1].name == "Nike Pegasus 39"
    assert catalogue.products[1].brand == "Nike"
    assert catalogue.products[1].price == Decimal("2499")
    assert not catalogue.products[1].is_for_sale

    row = database_session.execute(text("SELECT * FROM catalogues")).first()

    assert row.products == [  # type: ignore
        {"name": "Kit Kat Chunky", "brand": "Kit Kat", "price": 2.45},
        {
            "name": "Nike Pegasus 39",
            "brand": "Nike",
            "price": 2499,
            "is_for_sale": False,
        },
    ]


def test_sqlalchemy_serializes_value_in_pydantic_model_list_column_when_value_is_null(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(shipping_first_name="Matthew")

        database_session.add(cart)

    assert cart.products is None


def test_sqlalchemy_updates_value_in_pydantic_model_list_column_when_model_updates(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(
            shipping_first_name="Matthew",
            products=[
                Product(name="Kit Kat Chunky", brand="Kit Kat", price=Decimal("2.45")),
                Product(name="Nike Pegasus 39", brand="Nike", price=Decimal("2499")),
            ],
        )

        database_session.add(cart)

    assert len(cart.products) == 2

    assert cart.products[0].name == "Kit Kat Chunky"
    assert cart.products[0].brand == "Kit Kat"
    assert cart.products[0].price == Decimal("2.45")
    assert cart.products[0].is_for_sale

    assert cart.products[1].name == "Nike Pegasus 39"
    assert cart.products[1].brand == "Nike"
    assert cart.products[1].price == Decimal("2499")
    assert cart.products[1].is_for_sale

    with database_session.begin():
        cart.products[0].price = Decimal("4.78")

    assert cart.products[0].price == Decimal("4.78")


def test_sqlalchemy_updates_value_in_pydantic_model_list_column_when_model_is_added(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(
            shipping_first_name="Matthew",
            products=[
                Product(name="Kit Kat Chunky", brand="Kit Kat", price=Decimal("2.45")),
            ],
        )

        database_session.add(cart)

    assert len(cart.products) == 1

    assert cart.products[0].name == "Kit Kat Chunky"
    assert cart.products[0].brand == "Kit Kat"
    assert cart.products[0].price == Decimal("2.45")
    assert cart.products[0].is_for_sale

    with database_session.begin():
        cart.products.append(
            Product(
                name="G-Star Skinny Jeans - Size 32",
                brand="G-Star",
                price=Decimal("1699"),
            )
        )

    assert len(cart.products) == 2

    assert cart.products[0].name == "Kit Kat Chunky"
    assert cart.products[0].brand == "Kit Kat"
    assert cart.products[0].price == Decimal("2.45")
    assert cart.products[0].is_for_sale

    assert cart.products[1].name == "G-Star Skinny Jeans - Size 32"
    assert cart.products[1].brand == "G-Star"
    assert cart.products[1].price == Decimal("1699")
    assert cart.products[1].is_for_sale


def test_sqlalchemy_updates_value_in_pydantic_model_list_column_when_model_is_removed(
    database_session: Session,
) -> None:
    with database_session.begin():
        cart = Cart(
            shipping_first_name="Matthew",
            products=[
                Product(name="Kit Kat Chunky", brand="Kit Kat", price=Decimal("2.45")),
                Product(name="Nike Pegasus 39", brand="Nike", price=Decimal("2499")),
            ],
        )

        database_session.add(cart)

    assert len(cart.products) == 2

    assert cart.products[0].name == "Kit Kat Chunky"
    assert cart.products[0].brand == "Kit Kat"
    assert cart.products[0].price == Decimal("2.45")
    assert cart.products[0].is_for_sale

    assert cart.products[1].name == "Nike Pegasus 39"
    assert cart.products[1].brand == "Nike"
    assert cart.products[1].price == Decimal("2499")
    assert cart.products[1].is_for_sale

    with database_session.begin():
        del cart.products[1]

    assert len(cart.products) == 1

    assert cart.products[0].name == "Kit Kat Chunky"
    assert cart.products[0].brand == "Kit Kat"
    assert cart.products[0].price == Decimal("2.45")
    assert cart.products[0].is_for_sale
