import json
from datetime import datetime

from loguru import logger as log

from api.check_order_in_db import check_order_in_db
from api.create_order import create_order
from api.fees import get_fees
from api.good_in_order import create_good_in_order, good_in_order_by_order_id, update_good_in_order
from api.update_order import update_order
from api.update_parser_status_by_id import update_parser_status_by_id
from configs.env import LOG_FILE
from constants.status import ParserStatus
from etsy_api.orders import get_all_orders_by_shop_id
from parser.browser import get_browser, update_browser_shop_cookies
from parser.check_auth_cookie import check_auth_cookie
from parser.order_details import open_order_page_by_id, get_order_shipping, is_order_purchased_after_ad
from schemes.order import Order
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
PARSER_WAIT_TIME_IN_SECONDS = 60 * 15

if __name__ == "__main__":
    shops_data = get_parser_shops_data()
    browser = get_browser()

    for shop in shops_data:
        start_time_shop = datetime.now()
        log.info(f"Parsing shop {shop.shop_id} - {shop.shop_name}...")
        browser = update_browser_shop_cookies(browser, shop.shop_cookie)
        log.info(f"Updating parser {shop.parser_id} status to {ParserStatus.PARSING}...")
        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.PARSING,
        )
        log.success(f"Parser status updated.")

        # Check auth cookie for selenium
        is_cookie_expired = check_auth_cookie(browser)
        if is_cookie_expired:
            log.error(f"Parser auth cookie expired.")
            update_parser_status_by_id(
                parser_id=shop.parser_id,
                status=ParserStatus.COOKIE_EXPIRED,
            )
            continue

        # Get last 100 orders with etsy api
        log.info(f"Fetching 100 orders from shop {shop.shop_name}...")
        shop_orders, orders_count = get_all_orders_by_shop_id(
            etsy_shop_id=int(shop.etsy_shop_id),
            shop_id=shop.shop_id,
            limit=20,
            offset=50,
        )
        with open("orders.json", "w") as f:
            json.dump(shop_orders, f)
        log.success(f"Shop orders fetched.")

        orders_create: list[Order] = []
        orders_update: list[Order] = []
        # Get order details and split for creating and updating
        log.info(f"Fetching orders additional info...")
        for shop_order in shop_orders:
            # Getting fees for shop
            fees = get_fees(shop.shop_id)
            ######
            start_time_order = datetime.now()
            ######

            log.info(f"Check if order with id {shop_order['receipt_id']} exists...")
            existed_order = check_order_in_db(str(shop_order['receipt_id']))
            order, goods_in_order = format_order_data(
                order=shop_order,
                shop_id=shop.shop_id,
            )
            # Get order shipping and purchased after ad with selenium
            # TODO: fetch shipping of all orders with status like "Completed"
            if existed_order.id is None:
                log.info(f"Order with id {order.order_id} is not exists.")

                log.info(f"Fetching order shipping (order: {order.order_id})...")
                browser = open_order_page_by_id(browser, order.order_id)
                order.shipping = get_order_shipping(browser)
                log.success(f"Order shipping fetched: {order.shipping}.")

                log.info(f"Fetching order purchased after ad (order: {order.order_id})...")
                order.purchased_after_ad = is_order_purchased_after_ad(browser)
                log.success(f"Order purchased after ad fetched: {order.purchased_after_ad}")
                log.info(f"Creating parsed order...")
                new_order = create_order(order)
                if new_order:
                    log.success(f"Order created.")
                    log.info(f"Creating order goods")
                    for good_in_order in goods_in_order:
                        good_in_order.order_id = new_order.id
                        good = create_good_in_order(good_in_order)
                        if good:
                            log.success(
                                f"Successfully added good in order with order_id {good.order_id}, "
                                f"good_id {good.good_id}, amount {good.amount}, quantity {good.quantity}")
                        else:
                            log.error(
                                f"Couldn't add good in order with order_id {good_in_order.order_id}, good_id "
                                f"{good_in_order.good_id}, amount {good_in_order.amount}, "
                                f"quantity {good_in_order.quantity}")

                else:
                    log.error(f"Couldn't create order with id {order.order_id}")
            else:
                order.id = existed_order.id
                order.purchased_after_ad = existed_order.purchased_after_ad
                # order.shipping=
                log.info(f"Order with id {order.order_id} is exists.")
                log.info(f"Updating existed order...")
                new_order = update_order(order)
                log.success(f"Order updated.")
            ######
            end_time_order = datetime.now()
            log.critical(f"Order parsing time: {end_time_order - start_time_order}")
            ######

        log.success(f"Additional orders info fetched.")

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
    browser.quit()
