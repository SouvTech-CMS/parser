from sp_api.api import Orders
from sp_api.util import throttle_retry, load_all_pages
from sp_api.base import ApiResponse

from configs import settings
from constants.amazon_credentials import CREDENTIALS_ARG
from constants.amazon_dates import LAST_MONTH_DATE
from utils.safe_ratelimit_amazon import safe_rate_limit
from utils.format_datetime import is_iso_utc_z_format


class OrderClient:
    def __init__(self, log):
        self._order_cl = Orders()
        self._expanded_orders = []
        self.log = log


    @throttle_retry()
    @load_all_pages()
    def load_all_orders(self, **kwargs):
        return self._order_cl.get_orders(**kwargs)


    @throttle_retry()
    @load_all_pages()
    @safe_rate_limit(header_limit=True)
    def _load_all_items(self, order_id, **kwargs):
        return self._order_cl.get_order_items(order_id=order_id, **kwargs)


    def _get_all_items(self, order_id):
        items = []
        for i_page in self._load_all_items(order_id=order_id):
            for item in i_page.payload.get("OrderItems"):
                items.append(item)
        return items


    def get_orders(self, page: ApiResponse):

        try:
            for order in page.payload.get('Orders'):
                _order_id = order["AmazonOrderId"]

                self._expanded_orders.append({
                    "Order_data": order,
                    "Order_item_data": self._get_all_items(order_id=_order_id)
                })
        except Exception as e:
            self.log.

        return self._expanded_orders
