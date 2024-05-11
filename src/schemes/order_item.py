from pydantic import BaseModel


class GoodInOrderCreate(BaseModel):
    order_id: int | None = None
    good_id: int | None = None
    quantity: int | None = None
    amount: float | None = None


class GoodInOrder(BaseModel):
    id: int | None = None
    order_id: int | None = None
    good_id: int | None = None
    quantity: int | None = None
    amount: float | None = None


class GoodCreate(BaseModel):
    shop_id: int | None = None
    product_id: str | None = None
    listing_id: str | None = None
    name: str | None = None
    description: str | None = None


class Good(BaseModel):
    id: int | None = None
    shop_id: int | None = None
    product_id: str | None = None
    listing_id: str | None = None
    price: float | None = None
    name: str | None = None
    description: str | None = None
