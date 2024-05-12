from pydantic import BaseModel


class Fees(BaseModel):
    payment_processing_fee: str | None
    transaction_item: str | None
    transaction_shipping: str | None
    re_listing: float | None
    pack: float | None
