import time

import requests as req
from requests.exceptions import ConnectionError

from api.auth import authorization
from configs.env import API_URL
from schemes.order_item import GoodInOrder, GoodInOrderCreate


def good_in_order_by_order_id(order_id: int):
    list_of_goods_in_order = []
    try:
        response = req.get(
            f"{API_URL}/good_in_order/by_order_id/{order_id}",
            headers=authorization().model_dump(),
        )
    except Exception:
        time.sleep(1)
        return good_in_order_by_order_id(order_id)
    if response.status_code == 200:
        data = response.json()
        for good_in_order in data:
            list_of_goods_in_order.append(
                GoodInOrder(**response.json())
            )
        return list_of_goods_in_order
    return None


def create_good_in_order(good: GoodInOrderCreate) -> GoodInOrder | None:
    try:
        response = req.post(
            f"{API_URL}/good_in_order/",
            headers=authorization().model_dump(),
            json=good.model_dump()
        )
    except ConnectionError:
        return create_good_in_order(good)
    if response.status_code == 200:
        data = response.json()
        return GoodInOrder(**response.json())
    return None


def update_good_in_order(good: GoodInOrder) -> GoodInOrder | None:
    try:
        response = req.put(
            f"{API_URL}/good_in_order",
            headers=authorization().model_dump(),
            json=good.model_dump()
        )
    except ConnectionError:
        return update_good_in_order(good)
    if response.status_code == 200:
        data = response.json()
        return GoodInOrder(**response.json())
    return None
