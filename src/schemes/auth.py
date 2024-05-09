from pydantic import BaseModel


class Auth(BaseModel):
    Authorization: str


class AuthCode(BaseModel):
    code: str
