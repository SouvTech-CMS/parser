import requests as req

from api.auth import authorization
from configs.env import API_URL


def update_parser_status_by_id(parser_id: int, status: int):
    response = req.put(
        f"{API_URL}/parser/",
        headers=authorization().model_dump(),
        json={
            "id ": parser_id,
            "status": status,
        }
    )

    if response.status_code != 200:
        print(f"""
            Some error when updating parser status.
            Parser ID: {parser_id}.
            Status code: {response.status_code}
            Details: {response.text}
        """)
