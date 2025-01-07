import concurrent.futures
import pprint
import time
from datetime import datetime, timedelta

from loguru import logger as log

from api.order import upload_orders_data
from api.parser import update_parser_status_by_id
from configs.env import LOG_FILE
from constants.status import ParserStatus
from etsy_api.orders import get_all_orders_by_shop_id
from schemes.upload_order import UploadingOrderData, OrderData
from utils.format_order_data import format_order_data
from utils.parser_shops_data import get_parser_shops_data

log.add(
    LOG_FILE,
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
    serialize=True,
)

# Every 30 minutes
PARSER_WAIT_TIME_IN_SECONDS = 60 * 30


def process_single_shop(shop):
    now_hour = datetime.now().hour

    shop_error = False

    start_time_shop = datetime.now()
    log.info(f"Parsing shop {shop.shop_id} - {shop.shop_name}...")
    log.info(f"Updating parser {shop.parser_id} status to {ParserStatus.PARSING}...")
    update_parser_status_by_id(
        parser_id=shop.parser_id,
        status=ParserStatus.PARSING,
    )

    log.success(f"Parser status updated.")

    # Initializing constants
    that_month = True
    offset = 0
    date = datetime.now() - timedelta(days=30)
    weekday = datetime.now().weekday()
    ##########################

    while that_month:
        uploading_orders = UploadingOrderData(shop_id=shop.shop_id, orders_data=[])

        log.info(
            f"Fetching orders from {offset} to {offset + 100} from shop {shop.shop_name}..."
        )
        try:
            shop_orders, _ = get_all_orders_by_shop_id(
                etsy_shop_id=int(shop.etsy_shop_id),
                shop_id=shop.shop_id,
                limit=100,
                offset=offset,
            )
        except Exception as e:
            log.critical(f"Some error in getting info from ETSY API: {e}")
            pprint.pprint(e)
            update_parser_status_by_id(
                parser_id=shop.parser_id,
                status=ParserStatus.ETSY_API_ERROR,
            )
            shop_error = True
            break

        # Get order details and split for creating and updating
        for shop_order in shop_orders:

            order, goods_in_order, day, month, client, city = format_order_data(
                order=shop_order,
            )
            if day <= date.day and month == date.month:
                that_month = False
                break

            uploading_orders.orders_data.append(
                OrderData(
                    order=order,
                    client=client,
                    city=city,
                    order_items=goods_in_order,
                )
            )
        number_of_attempts = 0
        while number_of_attempts < 10:
            res = upload_orders_data(uploading_orders)
            if res:
                break
            number_of_attempts += 1
        if number_of_attempts == 10:
            log.critical(f"Some error on sending info to backend")
            update_parser_status_by_id(
                parser_id=shop.parser_id,
                status=ParserStatus.ETSY_API_ERROR,
            )
            shop_error = True
            break

        offset += 100

        if offset > 200:
            if now_hour < 20 and weekday in (5, 6):
                continue
            break

    if shop_error:
        log.error(f"Shop {shop.shop_id} - {shop.shop_name} parsed with error.")
        return
    log.info(
        f"Updating parser {shop.parser_id} status to {ParserStatus.OK_AND_WAIT}..."
    )

    update_parser_status_by_id(
        parser_id=shop.parser_id,
        status=ParserStatus.OK_AND_WAIT,
        last_parsed=datetime.now().timestamp(),
    )

    log.success(f"Parser status updated.")
    log.success(f"Shop {shop.shop_id} - {shop.shop_name} parsed.")
    end_time_shop = datetime.now()
    log.info(
        f"Shop  {shop.shop_id} - {shop.shop_name} parsing time: {end_time_shop - start_time_shop}"
    )


def etsy_api_parser():
    shops_data = get_parser_shops_data()

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


if __name__ == "__main__":
    while True:
        try:
            etsy_api_parser()
            time.sleep(PARSER_WAIT_TIME_IN_SECONDS)
        except Exception as e:
            log.error(f"Error on fetching orders {e}")
            time.sleep(900)
