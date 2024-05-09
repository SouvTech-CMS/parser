from pydantic import BaseModel


class Order(BaseModel):
    id: int | None
    shop_id: int
    order_id: str
    date: str
    quantity: int
    buyer_paid: float
    tax: float
    shipping: float | None
    purchased_after_ad: bool | None
