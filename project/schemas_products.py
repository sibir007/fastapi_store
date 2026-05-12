from datetime import datetime

from pydantic import BaseModel, Field, PlainSerializer


from decimal import Decimal
from typing import Annotated


class SProducIntBase(BaseModel):
    nom_id: int
    cost_price: Annotated[
        Decimal,
        PlainSerializer(float, when_used='json'),
        Field(
            description="cost price of product",
            )
        ]


class SProductIn(SProducIntBase):
    quantity: int


class SProductInDb(SProducIntBase):
    remainder: int


class SProsuctDbOut(BaseModel):
    id: int
    created: datetime
    nom_id: int
    cost_price: Annotated[
        Decimal,
        PlainSerializer(float, when_used='json'),
        Field(
            description="cost price of product",
            )
        ]
    remainder: int


class SProsuctDbOutFull(SProsuctDbOut):
    name: str
    description: str | None
    markup: Annotated[
        Decimal,
        PlainSerializer(float, when_used='json'),
        Field(
            description="markup in percent, for example 0.2 means 20% markup",
            )
        ]


class SNomenclatureIn(BaseModel):
    name: str
    description: str
    products: list[SProsuctDbOut] = []


class SNomenclatureOut(SNomenclatureIn):
    id: int
    created: datetime


class SProductSummaryOutBase(BaseModel):
    id: int
    name: str
    description: str | None
    total_remainder: int


class SProductSummaryOutAdmin(SProductSummaryOutBase):
    booked: int
    markup: Annotated[
        Decimal,
        PlainSerializer(float, when_used='json'),
        Field(
            description="markup in percent, for example 0.2 means 20% markup",
            )
        ]
    max_cost_price: Annotated[
        Decimal,
        PlainSerializer(float, when_used='json'),
        Field(
            description="max cost price of products with this nomenclature",
            )
        ]


class SProductSummaryOutByer(SProductSummaryOutBase):
    selling_price: Annotated[
        Decimal,
        PlainSerializer(float, when_used='json'),
        Field(
            description="selling price"
            )
        ]