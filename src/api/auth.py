from configs import settings
from schemes.auth import Auth


def authorization() -> Auth:
    return Auth(
        Authorization=f"Bearer {settings.API_AUTH_TOKEN}"
    )


