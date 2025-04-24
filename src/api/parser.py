import requests as req
from log.logger import logger

from api.auth import authorization
from configs import settings


def update_parser_status_by_id(
        parser_id: int, status: int, last_parsed: float | None = None
):
    data = {
        "id": parser_id,
        "status": status,
    }

    if last_parsed:
        data.update({"last_parsed": last_parsed})

    try:
        response = req.put(
            f"{settings.API_URL}/parser/", headers=authorization().model_dump(), json=data
        )

        if response.status_code != 200:
            raise ValueError(f"Unexpected status code: {response.status_code}")

    except ValueError:
        logger.error(
            f"""
                Some error when updating parser status.
                Parser ID: {parser_id}
                Status code: {response.status_code}
                Details: {response.json()['detail']}
            """
        )
    except Exception as e:
        logger.error(f"Some wrong with parser status updating = {e}")
