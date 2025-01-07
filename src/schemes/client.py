from pydantic import BaseModel


class Client(BaseModel):
    user_marketplace_id: str | None = None
    name: str | None = None
    email: str | None = None
