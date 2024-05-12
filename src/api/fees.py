import requests as req

from api.auth import authorization
from configs.env import API_URL
from schemes.fees import Fees


def get_fees(shop_id: int) -> Fees | None:
    try:
        response = req.get(
            f"{API_URL}/fees_and_expenses/{shop_id}",
            headers=authorization().model_dump(),
        )
    except ConnectionError:
        return get_fees(shop_id)
    if response.status_code == 200:
        data = response.json()
        return Fees(
            payment_processing_fee=data['payment_processing_fee'],
            transaction_item=data['transaction_item'],
            transaction_shipping=data['transaction_shipping'],
            re_listing=data['re_listing'],
            pack=data['pack'],
        )

    return None
