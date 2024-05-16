import requests as req
from loguru import logger as log
from requests.exceptions import ConnectionError

from api.auth import authorization
from configs.env import API_URL


def update_parser_status_by_id(parser_id: int, status: int):
    try:
        response = req.put(
            f"{API_URL}/parser/",
            headers=authorization().model_dump(),
            json={
                "id": parser_id,
                "status": status,
            }
        )
    except ConnectionError:
        return update_parser_status_by_id(parser_id, status)
    if response.status_code != 200:
        log.error(f"""
            Some error when updating parser status.
            Parser ID: {parser_id}
            Status code: {response.status_code}
            Details: {response.json()['detail']}
        """)
