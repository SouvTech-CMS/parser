import requests as req
from loguru import logger as log

from api.auth import authorization
from configs.env import API_URL


def update_parser_status_by_id(
    parser_id: int,
    status: int,
    last_parsed: float | None = None,
):
    data = {
        "id": parser_id,
        "status": status,
    }
    if last_parsed:
        data.update({"last_parsed": last_parsed})
    try:
        response = req.put(
            f"{API_URL}/parser/",
            headers=authorization().model_dump(),
            json=data,
        )
    except Exception as e:
        log.error(e)
        return update_parser_status_by_id(parser_id, status)
    if response.status_code != 200:
        log.error(
            f"""
            Some error when updating parser status.
            Parser ID: {parser_id}
            Status code: {response.status_code}
            Details: {response.json()['detail']}
            """
        )
