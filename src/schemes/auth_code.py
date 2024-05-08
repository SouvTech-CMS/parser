from pydantic import BaseModel


class AuthCode(BaseModel):
    code: str
