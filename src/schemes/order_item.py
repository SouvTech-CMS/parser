from pydantic import BaseModel


class GoodInOrder(BaseModel):
    uniquename: str | None = None
    quantity: int | None = None
    amount: float | None = None
    engraving_info: str | None = None
