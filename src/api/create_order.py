import requests as req

from api.auth import authorization
from configs.env import API_URL
from schemes.order import Order


def create_order(order: Order):
    response = req.post(
        f"{API_URL}/order/",
        headers=authorization().model_dump(),
        json=order,
    )
    if response.status_code != 200:
        print(f"""
            Some error when creating order.
            Order ID: {order.order_id}.
            Status code: {response.status_code}
            Details: {response.text}
        """)
