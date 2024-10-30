from datetime import datetime

from loguru import logger as log

from api.check_order_in_db import check_order_in_db
from api.create_order import create_order
from api.good_in_order import create_good_in_order
from api.update_order import update_order
from api.update_parser_status_by_id import update_parser_status_by_id
from configs.env import LOG_FILE
from constants.status import ParserStatus
from etsy_api.orders import get_all_orders_by_shop_id
from schemes.order import OrderUpdate
from utils.format_order_data import format_order_data
from utils.parser_shops_data import get_parser_shops_data

log.add(
    LOG_FILE,
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
    serialize=True
)

# Every 15 minutes
PARSER_WAIT_TIME_IN_SECONDS = 60 * 60 * 2

if __name__ == "__main__":
    shops_data = get_parser_shops_data()

    for shop in shops_data:
        start_time_shop = datetime.now()
        log.info(f"Parsing shop {shop.shop_id} - {shop.shop_name}...")
        log.info(f"Updating parser {shop.parser_id} status to {ParserStatus.PARSING}...")
        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.PARSING,
        )
        log.success(f"Parser status updated.")
        that_month = True
        offset = 0
        shop_orders, orders_count = get_all_orders_by_shop_id(
            etsy_shop_id=int(shop.etsy_shop_id),
            shop_id=shop.shop_id,
            limit=100,
            offset=offset,
        )
        while offset <= orders_count:
            log.info(f"Fetching orders from {offset} to {offset + 100} from shop {shop.shop_name}...")
            if offset:
                shop_orders, _ = get_all_orders_by_shop_id(
                    etsy_shop_id=int(shop.etsy_shop_id),
                    shop_id=shop.shop_id,
                    limit=100,
                    offset=offset,
                )

            # Get order details and split for creating and updating
            for shop_order in shop_orders:

                existed_order = check_order_in_db(str(shop_order['receipt_id']))
                order, goods_in_order, day, month = format_order_data(
                    order=shop_order,
                    shop_id=shop.shop_id,
                )
                # Adding order goods
                if existed_order is None:
                    log.info(f"Order with id {order.order_id} is not exists.")
                    # Shipping static
                    if order.quantity <= 10:
                        order.shipping = 5
                    elif order.quantity <= 20:
                        order.shipping = 6.5
                    elif order.quantity <= 30:
                        order.shipping = 15.6
                    else:
                        order.shipping = 18
                    ###################
                    new_order = create_order(order)
                    if new_order:
                        log.success(f"Order created.")
                        for good_in_order in goods_in_order:
                            good_in_order.order_id = new_order.id
                            good = create_good_in_order(good_in_order)

                    else:
                        log.error(f"Couldn't create order with id {order.order_id}")
                else:
                    if existed_order.status != order.status:
                        updating_order = OrderUpdate(
                            id=existed_order.id,
                            status=existed_order.status,
                            shipping=existed_order.shipping
                        )
                        if existed_order.status != order.status:
                            updating_order.status = order.status
                            log.info(f"Updating existed order status...")
                        if (updating_order.shipping != existed_order.shipping
                            or updating_order.status != existed_order.status):
                            new_order = update_order(updating_order)
                            log.success(f"Order data updated.")
                        else:
                            log.info(f"Here is no additional info to update.")
                    else:
                        log.info(f"Order {order.order_id} data up-to-date")
            offset += 100

        log.info(f"Updating parser {shop.parser_id} status to {ParserStatus.OK_AND_WAIT}...")
        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.OK_AND_WAIT,
        )
        log.success(f"Parser status updated.")
        log.success(f"Shop {shop.shop_id} - {shop.shop_name} parsed.")
        end_time_shop = datetime.now()
        log.critical(f"Shop parsing time: {end_time_shop - start_time_shop}")

    log.success(f"Parsing finished, wait {PARSER_WAIT_TIME_IN_SECONDS} seconds to repeat.")
