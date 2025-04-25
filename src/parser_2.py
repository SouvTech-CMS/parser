import json
from datetime import datetime

from api.parser import update_parser_status_by_id
from api.order import upload_orders_data
from constants.status import ParserStatus
from schemes.shop_data import ShopData
from schemes.upload_order import UploadingOrderData
from utils.parser_shops_data import get_parser_shops_data
from amazon_api.get_amazon_api import OrderClient

from constants.amazon_dates import LAST_MONTH_DATE, EARLIEST_DATE
from log.logger import logger

EXCEL_FILE = "data/check_point.xlsx"  # temporary
RETRY_LIMIT = 10


# TODO link on update refresh token don't forget!!!!

def process_single_shop(shop: ShopData):
    order_cl = OrderClient(shop=shop)
    created_after = LAST_MONTH_DATE
    shop_error = False
    offset = 0
    start_time_shop = datetime.now()
    weekday = datetime.now().weekday()
    now_hour = datetime.now().hour

    logger.info(f"Parsing shop {shop.shop_id} - {shop.shop_name}...")
    logger.info(
        f"Updating parser {shop.parser_id} status to {ParserStatus.PARSING}..."
    )

    update_parser_status_by_id(
        parser_id=shop.parser_id,
        status=ParserStatus.PARSING,
    )

    logger.success(f"Parser status updated.")

    for page_orders in order_cl.load_all_orders(CreatedAfter=created_after):
        """Every 100 orders after <CreatedAfter>"""

        uploading_orders = UploadingOrderData(shop_id=shop.shop_id, orders_data=[])

        logger.info(
            f"Fetching orders from {offset} to {offset + 100} from shop {shop.shop_name}..."
        )

        orders_data = order_cl.get_orders_with_items(page=page_orders)
        if orders_data is None:
            shop_error = True
            break

        uploading_orders.orders_data.extend(orders_data)

        try:
            upload_orders_data(uploading_orders)
        except:
            logger.critical(f"Some error on sending info to backend")
            update_parser_status_by_id(
                parser_id=shop.parser_id,
                status=ParserStatus.ETSY_API_ERROR,
            )
            shop_error = True

        offset += 100

        if offset > 200:
            if now_hour == 20 and weekday in (5, 6):
                continue
            break

    if shop_error:
        logger.error(f"Shop {shop.shop_id} - {shop.shop_name} parsed with error.")
        return
    logger.info(
        f"Updating parser {shop.parser_id} status to {ParserStatus.OK_AND_WAIT}..."
    )

    update_parser_status_by_id(
        parser_id=shop.parser_id,
        status=ParserStatus.OK_AND_WAIT,
        last_parsed=datetime.now().timestamp(),
    )

    logger.success(f"Parser status updated.")
    logger.success(f"Shop {shop.shop_id} - {shop.shop_name} parsed.")
    end_time_shop = datetime.now()
    logger.info(
        f"Shop  {shop.shop_id} - {shop.shop_name} parsing time: {end_time_shop - start_time_shop}"
    )

#TODO func
def etsy_api_parser():
    shops_data = get_parser_shops_data()
    # for shop in shops_data:
    #     etsy_api = get_etsy_api(shop.shop_id)
    # Используем ThreadPoolExecutor для параллельной обработки
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Запускаем обработку каждого магазина в отдельном потоке
        futures = [executor.submit(process_single_shop, shop) for shop in shops_data]
        # Ждем завершения всех задач
        concurrent.futures.wait(futures)
        # Проверяем, были ли исключения
        for future in futures:
            if future.exception():
                log.error(f"Error in thread: {future.exception()}")
    log.success(f"Parsed all shops waiting {PARSER_WAIT_TIME_IN_SECONDS} to repeat")


# TODO: сделать чтобы файлы с кредами не писались в файл в многопотоке
#TODO Func

if __name__ == "__main__":
    while True:
        try:
            etsy_api_parser()
            time.sleep(PARSER_WAIT_TIME_IN_SECONDS)
        except Exception as e:
            log.error(f"Error on fetching orders {e}")
            time.sleep(900)
