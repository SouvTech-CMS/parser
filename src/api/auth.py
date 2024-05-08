import requests as req

from configs.env import API_AUTH_TOKEN
from schemes.auth import Auth


def authorization() -> Auth:
    return Auth(
        Authorization=f"Bearer {API_AUTH_TOKEN}"
    )
