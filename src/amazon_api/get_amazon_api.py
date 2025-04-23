from sp_api.api import Orders
from sp_api.util import throttle_retry, load_all_pages

from configs import settings
from constants.amazon_credentials import CREDENTIALS_ARG
from constants.amazon_dates import LAST_MONTH
from utils.safe_ratelimit_amazon import safe_rate_limit
from utils.format_datetime import is_iso_utc_z_format


LIMIT=100



class OrderClient:
    def __init__(self, log):
        self._order_cl = Orders()
        self._expanded_orders = []
        self.log = log




    @throttle_retry()
    @load_all_pages()
    def _load_all_orders(self, **kwargs):
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


    def get_orders(self, created_after: str):
        """
        Args:
        created_after: iso6108 format with Z
        """

        if not is_iso_utc_z_format(created_after):
            created_after = LAST_MONTH

        for page in self._load_all_orders(CreatedAfter=created_after):

            for order in page.payload.get('Orders'):
                _order_id = order["AmazonOrderId"]

                self._expanded_orders.append({
                    "Order_data": order,
                    "Order_item_data": self._get_all_items(order_id=_order_id)
                })

        return self._expanded_orders
