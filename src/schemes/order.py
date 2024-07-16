from pydantic import BaseModel


class Order(BaseModel):
    id: int | None = None
    status: str | None = None
    shop_id: int | None = None
    order_id: str | None = None
    date: str | None = None
    quantity: int | None = None
    buyer_paid: float | None = None
    tax: float | None = None
    shipping: float | None = None
    full_fee: float | None = None
    profit: float | None = None


class OrderUpdate(BaseModel):
    id: int | None
    status: str | None
    shipping: float | None
