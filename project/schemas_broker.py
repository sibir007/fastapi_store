from pydantic import BaseModel

from project.schemas_auth import SUserOut


class BrokerExeption(BaseModel):
    code: int
    detailes: str


class BorkerResoultBase(BaseModel):
    exeption: BrokerExeption | None = None


class UserBrokerResult(BorkerResoultBase):
    result: SUserOut | None = None