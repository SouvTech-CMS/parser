from pydantic import BaseModel


class Order(BaseModel):
    id: int | None = None
    shop_id: int | None
    order_id: str | None
    date: str | None
    quantity: int | None
    buyer_paid: float | None
    tax: float | None
    shipping: float | None = None
    purchased_after_ad: bool | None = None
    full_fee: float | None = None
    profit: float | None = None
