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
            status=order_data['status'],
            shop_id=order_data['shop_id'],
            order_id=order_data['order_id'],
            date=order_data['date'],
            quantity=order_data['quantity'],
            buyer_paid=order_data['buyer_paid'],
            tax=order_data['tax'],
            shipping=order_data['shipping'],
            purchased_after_ad=order_data['purchased_after_ad'],
            full_fee=order_data['full_fee'],
            profit=order_data['profit']
        )

    return None
