from pydantic import BaseModel

class Parser(BaseModel):
    id: int
    shop_id: int
    status: int
    command: int
    last_parsed: str
    frequency: int
    # TODO delete this params
    auth_cookie: str
    cookie_edited: str
