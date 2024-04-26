from pydantic import BaseModel


class AuthToken(BaseModel):
    access_token: str
    expiry: int
    refresh_token: str
