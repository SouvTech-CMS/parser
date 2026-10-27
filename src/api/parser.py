import time

import requests as req
from loguru import logger as log

from api.auth import authorization
from configs.env import API_URL
from constants.backend import (
    BACKEND_REQUEST_TIMEOUT_IN_SECONDS,
    BACKEND_RETRY_DELAY_IN_SECONDS,
    UPDATE_PARSER_STATUS_ATTEMPTS,
)


def update_parser_status_by_id(
        parser_id: int,
        status: int,
        last_parsed: float | None = None,
):
    log.info(
        f"Updating parser {parser_id} status to {status}..."
    )
    data = {
        "id": parser_id,
        "status": status,
    }
    if last_parsed:
        data.update({"last_parsed": last_parsed})

    # NOTE: status is informational, so after last failed attempt just go on parsing
    for attempt in range(1, UPDATE_PARSER_STATUS_ATTEMPTS + 1):
        try:
            response = req.put(
                f"{API_URL}/parser/",
                headers=authorization().model_dump(),
                json=data,
                timeout=BACKEND_REQUEST_TIMEOUT_IN_SECONDS,
            )
        except req.RequestException as e:
            log.error(
                f"Some error when updating parser {parser_id} status "
                f"(attempt {attempt}/{UPDATE_PARSER_STATUS_ATTEMPTS}): {e}"
            )
            if attempt < UPDATE_PARSER_STATUS_ATTEMPTS:
                time.sleep(BACKEND_RETRY_DELAY_IN_SECONDS)
            continue

        if response.status_code != 200:
            log.error(
                f"""
                Some error when updating parser status.
                Parser ID: {parser_id}
                Status code: {response.status_code}
                Details: {response.text}
                """
            )
        else:
            log.success(f"Parser {parser_id} status updated.")
        return
