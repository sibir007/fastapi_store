from pydantic import BaseModel

from project.schemas import SBool
from project.schemas_auth import SUserOut, STopupOut
from project.schemas_cart import SCartItem, SCart
from project.schemas_orders import SOrderOut
from project.schemas_products import SProductSummaryOutByer


class SServiceExeption(BaseModel):
    code: int
    detailes: str


class SServiceResoultBase[T](BaseModel):
    resoult: T | None = None
    exeption: SServiceExeption | None = None


class SUserServiceResult(SServiceResoultBase[SUserOut]):
    pass


# type SVerifyReqversBrokerResult = SBorkerResoultBase[SBool] 

class SVerifyReqversServiceResult(SServiceResoultBase[SBool]):
    pass


class STopupServiceResult(SServiceResoultBase[STopupOut]):
    pass


class SCartServiceResult(SServiceResoultBase[SCart]):
    pass


class SCatrItemServiceResoult(SServiceResoultBase[SCartItem]):
    pass


class SProductsSummaryOutByerServiceResoult(
    SServiceResoultBase[list[SProductSummaryOutByer]]
):
    pass

class SOrdersServiceResult(SServiceResoultBase[list[SOrderOut]]):
    pass 

class SOrderServiceResult(SServiceResoultBase[SOrderOut]):
    pass