import requests as req

from api.auth import authorization
from configs.env import API_URL
from schemes.parser_info import Parser


def get_parser_info(parser_id: int) -> Parser | None:
    data = req.get(
        f"{API_URL}/parser/{parser_id}",
        headers=authorization().model_dump(),
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
            cookie_edited=data["cookie_edited"]
        )
    return None


def update_parser_command_to_default(parser_id: int):
    data = req.put(
        f"{API_URL}/parser",
        headers=authorization().model_dump(),
        json={
            "id": parser_id,
            "command": 0,
        }
    )
    if data.status_code != 200:
        print(f"Error with updating "
              f"parser status to default"
              f"Status code: {data.status_code}"
              f"Text: {data.text}"
              )
