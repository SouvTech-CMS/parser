from sp_api.api import Orders
from sp_api.util import throttle_retry, load_all_pages
from sp_api.base import ApiResponse

import pprint

from constants.amazon_credentials import CREDENTIALS_ARG
from constants.status import ParserStatus
from utils.safe_ratelimit_amazon import safe_rate_limit
from utils.format_order_data import format_order_data
from schemes.shop_data import ShopData
from schemes.upload_order import OrderData
from api.parser import update_parser_status_by_id
from log.logger import logger


class OrderClient:
    def __init__(self, shop: ShopData):
        self.order_api = Orders(**CREDENTIALS_ARG)
        self._list_orders_data = []
        self.shop = shop


    def _get_all_items(self, order_id) -> list:
        items = []
        for i_page in self._load_all_items(order_id=order_id):
            for item in i_page.payload.get("OrderItems"):
                items.append(item)
        return items


    @throttle_retry()
    @load_all_pages()
    def load_all_orders(self, **kwargs):
        return self.order_api.get_orders(**kwargs)


    @throttle_retry()
    @load_all_pages()
    @safe_rate_limit(header_limit=True)
    def _load_all_items(self, order_id, **kwargs):
        return self.order_api.get_order_items(order_id=order_id, **kwargs)


    def get_orders_with_items(self, page: ApiResponse) -> list[OrderData] | None:
        try:
            for order in page.payload.get('Orders'):
                _order_id = order["AmazonOrderId"]
                logger.info(f"formating order ID: {_order_id}")
                order_data = format_order_data(
                    order=order,
                    items=self._get_all_items(order_id=_order_id)
                )
                self._list_orders_data.append(order_data)
        except Exception as e:
            logger.critical(f"Some error in getting info from Amazon SP API: {e}")
            pprint.pprint(e)
            update_parser_status_by_id(
                parser_id=self.shop.parser_id,
                status=ParserStatus.OK_AND_WAIT
            )
            return None

        return self._list_orders_data
