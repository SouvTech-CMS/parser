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
from schemes.shop_data import ShopData
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

# Every minute
PARSER_WAIT_TIME_IN_SECONDS = 60 * 1
ORDERS_PER_REQUEST = 10
ORDERS_PER_REQUEST_PER_MONTH = 100
DEFAULT_OFFSET = 9


class ShopError(Exception):
    parser_id: int


class BackendError(Exception):
    pass


def upload_order_data_to_backend(shop: ShopData, uploading_data: UploadingOrderData):
    number_of_attempts = 0
    while number_of_attempts < 10:
        res = upload_orders_data(uploading_data)
        if res:
            break
        number_of_attempts += 1
    if number_of_attempts == 10:
        log.critical(f"Some error on sending info to backend")
        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.ETSY_API_ERROR,
        )
        raise BackendError


def parse_per_month(shop: ShopData):
    log.info("Getting orders per month")
    # Initializing constants
    that_month = True
    offset = 0
    date = datetime.now() - timedelta(days=30)
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
            raise ShopError
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
        upload_order_data_to_backend(shop, uploading_orders)
        offset += 100


def process_single_shop(shop):
    try:
        now = datetime.now()

        start_time_shop = datetime.now()
        log.info(f"Parsing shop {shop.shop_id} - {shop.shop_name}...")
        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.PARSING,
        )

        # Initializing constants
        weekday = datetime.now().weekday()
        ##########################

        uploading_orders = UploadingOrderData(shop_id=shop.shop_id, orders_data=[])

        log.info(
            f"Fetching {ORDERS_PER_REQUEST} orders from shop {shop.shop_name}..."
        )

        try:
            shop_orders, _ = get_all_orders_by_shop_id(
                etsy_shop_id=int(shop.etsy_shop_id),
                shop_id=shop.shop_id,
                limit=ORDERS_PER_REQUEST,
                offset=DEFAULT_OFFSET,
            )
        except Exception as e:
            raise ShopError(e)

        # Get order details and split for creating and updating
        for shop_order in shop_orders:
            order, goods_in_order, day, month, client, city = format_order_data(
                order=shop_order,
            )
            uploading_orders.orders_data.append(
                OrderData(
                    order=order,
                    client=client,
                    city=city,
                    order_items=goods_in_order,
                )
            )
        upload_order_data_to_backend(shop, uploading_orders)
        if now.hour == 19 and now.minute < 3 and weekday in (5, 6):
            parse_per_month(shop)

        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.OK_AND_WAIT,
            last_parsed=datetime.now().timestamp(),
        )

        log.success(f"Shop {shop.shop_id} - {shop.shop_name} parsed.")
        log.info(
            f"Shop  {shop.shop_id} - {shop.shop_name} parsing time: {datetime.now() - start_time_shop}"
        )
    except ShopError as e:
        log.critical(f"Some error in getting info from ETSY API: {e}")
        pprint.pprint(e)
        log.error(f"Shop {shop.shop_id} - {shop.shop_name} parsed with error.")
        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.ETSY_API_ERROR,
        )
    except BackendError as ex:
        log.critical(f"Some error on backend requests, parser: {shop.parser_id}")
        pprint.pprint(ex)

    except Exception as ex:
        log.critical(ex)
        pprint.pprint(ex)


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


# TODO: сделать чтобы файлы с кредами не писались в файл в многопотоке

if __name__ == "__main__":
    while True:
        try:
            etsy_api_parser()
            time.sleep(PARSER_WAIT_TIME_IN_SECONDS)
        except Exception as e:
            log.error(f"Error on fetching orders {e}")
            time.sleep(900)
