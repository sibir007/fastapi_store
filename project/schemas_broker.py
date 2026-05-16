from pydantic import BaseModel

from project.schemas import SBool
from project.schemas_auth import STopupOut
from project.schemas_auth import SUserOut
from project.schemas_cart import SCartItem, SCart
from project.schemas_products import SProductSummaryOutByer


class SBrokerExeption(BaseModel):
    code: int
    detailes: str


class SBorkerResoultBase[T](BaseModel):
    resoult: T | None = None
    exeption: SBrokerExeption | None = None


class SUserBrokerResult(SBorkerResoultBase[SUserOut]):
    pass


# type SVerifyReqversBrokerResult = SBorkerResoultBase[SBool] 

class SVerifyReqversBrokerResult(SBorkerResoultBase[SBool]):
    pass


class STopupBrokerResult(SBorkerResoultBase[STopupOut]):
    pass


class SCartBrokerResult(SBorkerResoultBase[SCart]):
    pass


class SCatrItemBrokerResoult(SBorkerResoultBase[SCartItem]):
    pass


class SProductsSummaryOutByerBrokerResoult(
    SBorkerResoultBase[list[SProductSummaryOutByer]]
):
    pass
