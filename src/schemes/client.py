from pydantic import BaseModel


class Client(BaseModel):
    shop_client_id: str | None = None
    name: str | None = None
    email: str | None = None
