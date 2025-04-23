from sp_api.api import Orders
from sp_api.util import throttle_retry, load_all_pages
from sp_api.base import ApiResponse
import pprint

from configs import settings
from constants.amazon_credentials import CREDENTIALS_ARG
from constants.amazon_dates import LAST_MONTH_DATE
from constants.status import ParserStatus
from utils.safe_ratelimit_amazon import safe_rate_limit
from utils.format_datetime import is_iso_utc_z_format
from api.parser import update_parser_status_by_id
from log.logger import logger
from schemes.shop_data import ShopData


class OrderClient:
    def __init__(self, shop: ShopData):
        self._expanded_orders = []
        self.shop = shop

    def _get_all_items(self, order_id):
        items = []
        for i_page in self._load_all_items(order_id=order_id):
            for item in i_page.payload.get("OrderItems"):
                items.append(item)
        return items


    @throttle_retry()
    @load_all_pages()
    def load_all_orders(self, **kwargs):
        return self.get_orders(**kwargs)


    @throttle_retry()
    @load_all_pages()
    @safe_rate_limit(header_limit=True)
    def _load_all_items(self, order_id, **kwargs):
        return self._get_order_items(order_id=order_id, **kwargs)





    def get_orders(self, page: ApiResponse):
        try:
            for order in page.payload.get('Orders'):
                _order_id = order["AmazonOrderId"]

                self._expanded_orders.append({
                    "Order_data": order,
                    "Order_item_data": self._get_all_items(order_id=_order_id)
                })
        except Exception as e:
            logger.critical(f"Some error in getting info from Amazon SP API: {e}")
            pprint.pprint(e)
            update_parser_status_by_id(
                parser_id=self.shop.parser_id,
                status=ParserStatus.OK_AND_WAIT
            )
            #TODO: retrurn shop_error

        return self._expanded_orders
