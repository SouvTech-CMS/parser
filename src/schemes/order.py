from pydantic import BaseModel


class Order(BaseModel):
    order_id: str | None = None
    status: str | None = None
    date: str | None = None
    quantity: int | None = None
    buyer_paid: float | None = None
    tax: float | None = None
    receipt_shipping_id: str | None = None
    tracking_code: str | None = None
