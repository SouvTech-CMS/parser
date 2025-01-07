import requests as req
from loguru import logger as log

from api.auth import authorization
from configs.env import API_URL
from schemes.upload_order import UploadingOrderData


def upload_orders_data(orders: UploadingOrderData) -> bool:
    response = req.post(
        f"{API_URL}/parser/orders/upload/",
        headers=authorization().model_dump(),
        json=orders.model_dump(),
    )

    if response.status_code != 200:
        log.error(
            f"""
            Some error when uploading orders data, status code: {response.status_code}
        """
        )
        return False
    return True
