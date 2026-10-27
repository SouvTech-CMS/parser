import requests as req
from loguru import logger as log

from api.auth import authorization
from configs.env import API_URL
from constants.backend import BACKEND_REQUEST_TIMEOUT_IN_SECONDS
from schemes.upload_order import UploadingOrderData


def upload_orders_data(orders: UploadingOrderData) -> bool:
    try:
        response = req.post(
            f"{API_URL}/parser/orders/upload/",
            headers=authorization().model_dump(),
            json=orders.model_dump(),
            timeout=BACKEND_REQUEST_TIMEOUT_IN_SECONDS,
        )
    except req.RequestException as e:
        log.error(f"Some error when uploading orders data: {e}")
        return False

    if response.status_code != 200:
        log.error(
            f"""
            Some error when uploading orders data, status code: {response.status_code}
        """
        )
        return False
    return True
