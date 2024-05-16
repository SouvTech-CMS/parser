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
    except ConnectionError:
        time.sleep(1)
        return good_in_order_by_order_id(order_id)
    if response.status_code == 200:
        data = response.json()
        for good_in_order in data:
            list_of_goods_in_order.append(
                GoodInOrder(
                    id=good_in_order['id'],
                    order_id=good_in_order['order_id'],
                    good_id=good_in_order['good_id'],
                    quantity=good_in_order['quantity'],
                    amount=good_in_order['amount'],
                )
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
        return GoodInOrder(
            id=data['id'],
            order_id=data['order_id'],
            good_id=data['good_id'],
            quantity=data['quantity'],
            amount=data['amount'],
        )
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
        return GoodInOrder(
            id=data['id'],
            order_id=data['order_id'],
            good_id=data['good_id'],
            quantity=data['quantity'],
            amount=data['amount'],
        )
    return None