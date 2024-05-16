import requests as req
from requests.exceptions import ConnectionError

from api.auth import authorization
from configs.env import API_URL
from schemes.order import Order


def check_order_in_db(order_in_shop_id: str) -> Order | None:
    try:
        response = req.get(
            f"{API_URL}/order/in_shop_id/{order_in_shop_id}",
            headers=authorization().model_dump(),
        )
    except ConnectionError:
        return check_order_in_db(order_in_shop_id)
    if response.status_code == 200:
        order_data = response.json()
        return Order(
            id=order_data['id'],
            purchased_after_ad=order_data['purchased_after_ad'],
            shipping=order_data['shipping'],
        )

    return None
