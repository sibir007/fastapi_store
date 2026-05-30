import enum

from pydantic import BaseModel


class SBool(BaseModel):
    result: bool


class OrderStatus(enum.Enum):
    WAITING = "waiting" # waiting for payment
    CANCELED = "canceled"
    PAID = "paid"
    COMPLETED = "completed"


class SUsername(BaseModel):
    username: str
