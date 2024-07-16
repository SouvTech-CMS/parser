import requests as req

from api.auth import authorization
from configs.env import API_URL
from schemes.order import Order


def check_order_in_db(order_in_shop_id: str) -> Order | None:
    try:
        response = req.get(
            f"{API_URL}/order/in_shop_id/{order_in_shop_id}",
            headers=authorization().model_dump(),
        )
    except Exception:
        return check_order_in_db(order_in_shop_id)
    if response.status_code == 200:
        order_data = response.json()
        return Order(**order_data)

    return None
