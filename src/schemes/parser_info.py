from pydantic import BaseModel


class Parser(BaseModel):
    id: int
    shop_id: str
    status: int
    command: int
    last_parsed: str
    frequency: int
    auth_cookie: str
    token_edited: str
