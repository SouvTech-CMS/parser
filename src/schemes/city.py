from pydantic import BaseModel


class City(BaseModel):
    name: str | None = None
    state: str | None = None
    country: str | None = None
