import requests as req

from api.auth import authorization
from configs import settings
from schemes.upload_order import UploadingOrderData

from log.logger import logger
from utils.retry import retry


@retry()
def upload_orders_data(orders: UploadingOrderData):
    logger.info("Posting data to backend...")
    response = req.post(
        f"{settings.API_URL}/parser/orders/upload/",
        headers=authorization().model_dump(),
        json=orders.model_dump(),
    )

    if response.status_code != 200:
        logger.error(
            f"""
            Some error when uploading orders data, status code: {response.status_code}
        """
        )
        response.raise_for_status()



