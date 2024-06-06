from pydantic import BaseModel


class Parser(BaseModel):
    id: int
    shop_id: int
    status: int
    command: int
    last_parsed: str
