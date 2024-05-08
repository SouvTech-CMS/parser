import requests as req

from api.auth import authorization
from configs.env import API_URL
from schemes.parser_info import Parser


def get_parser_info(parser_id: int) -> Parser | None:
    data = req.get(
        f"{API_URL}/parser",
        headers=authorization().model_dump(),
        json={
            "parser_id ": parser_id
        }
    )
    if data.status_code == 200:
        data = data.json()
        return Parser(
            id=data["id"],
            shop_id=data["shop_id"],
            status=data["status"],
            command=data["command"],
            last_parsed=data["last_parsed"],
            frequency=data["frequency"],
            auth_cookie=data["auth_cookie"],
            token_edited=data["token_edited"]
        )
    return None


