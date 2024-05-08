from pydantic import BaseModel


class Order(BaseModel):
    shop_id: int
    order_id: str
    date: str
    quantity: int
    buyer_paid: float
    tax: float
    shipping: float
    purchased_after_ad: bool
