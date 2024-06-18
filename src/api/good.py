import requests as req
from loguru import logger as log
from requests.exceptions import ConnectionError

from api.auth import authorization
from configs.env import API_URL
from schemes.order_item import Good, GoodCreate


def check_good_in_base(shop_id: int, uniquename: str) -> Good | None:
    try:
        response = req.get(
            f"{API_URL}/good/get_by_uniquename_and_shop_id/",
            headers=authorization().model_dump(),
            params={
                "uniquename": uniquename,
                "shop_id": shop_id
            }
        )
    except Exception:
        return check_good_in_base(shop_id, uniquename)
    if response.status_code != 200:
        return None
    data = response.json()
    return Good(**data)


def good_create(good: GoodCreate) -> Good | None:
    try:

        response = req.post(
            f"{API_URL}/good",
            headers=authorization().model_dump(),
            json=good.model_dump()
        )
    except ConnectionError:
        return good_create(good)
    if response.status_code == 200:
        data = response.json()
        return Good(**data)

    log.critical("Couldn't create good ")
    return None
