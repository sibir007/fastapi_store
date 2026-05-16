from pydantic import BaseModel


class SBool(BaseModel):
    result: bool