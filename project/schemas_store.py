from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer


from decimal import Decimal
from typing import Annotated

from project.schemas_orders import SOrderItem

class SNomId(BaseModel):
    nom_id: int


class SProducIntBase(SNomId):
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
    model_config = ConfigDict(from_attributes=True)
    
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

class SSaleItemOut(BaseModel):
    nom_id: int
    quantity: int
    byer_price: Annotated[
        Decimal,
        PlainSerializer(float, when_used='json'),
        Field(
            description="byer price of product in that sale"
            )
        ]


class SSaleBase(BaseModel):
    order_id: int

class SSaleIn(SSaleBase):
    items: list[SOrderItem]

class SSaleOut(SSaleBase):
    model_config = ConfigDict(from_attributes=True)

    created: datetime
    id: int
    # order_id: int
    # items: list[SSaleItemOut]


