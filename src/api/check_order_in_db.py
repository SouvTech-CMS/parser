import requests as req

from api.auth import authorization
from configs.env import API_URL


def check_order_in_db(order_in_shop_id: str) -> int | None:
    response = req.get(
        f"{API_URL}/order/in_shop_id/{order_in_shop_id}",
        headers=authorization().model_dump(),
    )
    if response.status_code == 200:
        order_data = response.json()
        return order_data['id']

    return None
