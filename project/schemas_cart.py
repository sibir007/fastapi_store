
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class SCartItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nom_id: int
    quantity: Annotated[int, Field(ge=0)]

class SCartItemIn(SCartItem):
    username: str

class SCartItemDbOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    nom_id: int
    quantity: int

class SCart(BaseModel):
    items: list[SCartItem]


class SCartReq(BaseModel):
    username: str