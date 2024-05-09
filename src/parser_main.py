from api.check_order_in_db import check_order_in_db
from api.create_order import create_order
from api.update_order import update_order
from api.update_parser_status_by_id import update_parser_status_by_id
from constants.status import ParserStatus
from etsy_api.orders import get_all_orders_by_shop_id
from parser.browser import get_browser, update_browser_shop_cookies
from parser.check_auth_cookie import check_auth_cookie
from parser.order_details import open_order_page_by_id, get_order_shipping, is_order_purchased_after_ad
from schemes.order import Order
from utils.format_order_data import format_order_data
from utils.parser_shops_data import get_parser_shops_data

if __name__ == "__main__":
    shops_data = get_parser_shops_data()
    browser = get_browser()

    for shop in shops_data:
        browser = update_browser_shop_cookies(browser)

        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.PARSING,
        )

        # Check auth cookie for selenium
        is_cookie_expired = check_auth_cookie(browser)
        if is_cookie_expired:
            update_parser_status_by_id(
                parser_id=shop.parser_id,
                status=ParserStatus.COOKIE_EXPIRED,
            )
            continue

        # Get last 100 orders with etsy api
        shop_orders = get_all_orders_by_shop_id(shop.etsy_shop_id)
        orders_create: list[Order] = []
        orders_update: list[Order] = []
        # Get order details and split for creating and updating
        for shop_order in shop_orders:
            order = format_order_data(
                order=shop_order,
                shop_id=shop.shop_id,
            )
            existed_order_id = check_order_in_db(order.order_id)

            # Get order shipping and purchased after ad with selenium
            if existed_order_id is None:
                browser = open_order_page_by_id(browser, order.order_id)

                order_shipping = get_order_shipping(browser)
                order.shipping = order_shipping

                order_purchased_after_ad = is_order_purchased_after_ad(browser)
                order.purchased_after_ad = order_purchased_after_ad

                orders_create.append(order)
                continue

            order.id = existed_order_id
            orders_update.append(order)

        # Create order in db
        for new_order in orders_create:
            create_order(new_order)

        # Update order in db
        for updated_order in orders_update:
            update_order(updated_order)

        update_parser_status_by_id(
            parser_id=shop.parser_id,
            status=ParserStatus.OK_AND_WAIT,
        )

    print("Closing process successfully...")
    browser.quit()
