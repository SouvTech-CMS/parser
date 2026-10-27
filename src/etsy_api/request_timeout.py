import requests
from requests.adapters import HTTPAdapter

# NOTE: etsyv3 sends requests without timeout, so a stuck connection to Etsy
# hangs the shop thread forever and the whole cycle waits for it.
# (connect, read): read timeout is per socket read, not for the whole response
ETSY_REQUEST_TIMEOUT_IN_SECONDS = (10, 60)


class TimeoutHTTPAdapter(HTTPAdapter):
    """Applies default timeout to requests sent without explicit one."""

    def send(self, request, timeout=None, **kwargs):
        if timeout is None:
            timeout = ETSY_REQUEST_TIMEOUT_IN_SECONDS
        return super().send(request, timeout=timeout, **kwargs)


def set_etsy_request_timeout(session: requests.Session):
    adapter = TimeoutHTTPAdapter()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
