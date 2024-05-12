import requests as req
from loguru import logger as log

from api.auth import authorization
from configs.env import API_URL
from schemes.order import Order


def update_order(order: Order):
    try:
        response = req.put(
            f"{API_URL}/order/",
            headers=authorization().model_dump(),
            json=order.model_dump(),
        )
    except ConnectionError:
        return update_order(order)
    if response.status_code != 200:
        log.error(f"""
            Some error when creating order.
            Order ID: {order.order_id}.
            Status code: {response.status_code}
            Details: {response.text}
        """)
