import pprint
import time
from datetime import datetime

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


def etsy_api_parser():
    shops_data = get_parser_shops_data()
    now_hour = datetime.now().hour
    for shop in shops_data:

        shop_error = False

        start_time_shop = datetime.now()
        log.info(f"Parsing shop {shop.shop_id} - {shop.shop_name}...")
        log.info(
            f"Updating parser {shop.parser_id} status to {ParserStatus.PARSING}..."
        )
        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.PARSING,
        )

        log.success(f"Parser status updated.")

        # Initializing constants
        offset = 0
        ##########################
        try:
            shop_orders, orders_count = get_all_orders_by_shop_id(
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
            break
        while offset <= orders_count:
            uploading_orders = UploadingOrderData(shop_id=shop.shop_id, is_full_data_updating=True, orders_data=[])

            log.info(
                f"Fetching orders from {offset} to {offset + 100} from shop {shop.shop_name}..."
            )
            if offset:
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

                uploading_orders.orders_data.append(
                    OrderData(
                        order=order,
                        client=client,
                        city=city,
                        order_items=goods_in_order,
                    )
                )

            upload_orders_data(uploading_orders)

            offset += 100

        if shop_error:
            continue

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
        log.info(f"Shop parsing time: {end_time_shop - start_time_shop}")

    log.success(
        f"Parsing finished, wait {PARSER_WAIT_TIME_IN_SECONDS} seconds to repeat."
    )


if __name__ == "__main__":

    try:
        etsy_api_parser()
        time.sleep(PARSER_WAIT_TIME_IN_SECONDS)
        time.sleep(900)
    except Exception as e:
        log.error(f"Error on fetching orders {e}")
        time.sleep(900)
