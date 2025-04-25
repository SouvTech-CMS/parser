from pydantic import BaseModel


class Auth(BaseModel):
    Authorization: str

