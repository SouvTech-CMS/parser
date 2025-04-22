from sp_api.api import Orders
from sp_api.util import throttle_retry, load_all_pages
from datetime import datetime, timezone
from loguru import logger

from configs import settings
from utils.safe_ratelimit_amazon import safe_rate_limit

CREDENTIALS = dict(
    lwa_app_id=settings.LWA_APP_ID,
    lwa_client_secret=settings.LWA_CLIENT_SECRET
)

LAST_UPDATE_BEFORE=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
#first order was offer in 2024/2/17
CREATED_AFTER = datetime(2024, 1, 1).isoformat().replace("+00:00", 'Z')
LIMIT=100



class OrderClient:
    def __init__(self):
        self._order_cl = Orders(credentials=CREDENTIALS,
                                refresh_token=settings.SP_API_REFRESH_TOKEN)
        self._expanded_orders = []


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


    def get_orders(self):
        for page in self._load_all_orders(CreatedAfter=CREATED_AFTER):
            for order in page.payload.get('Orders'):
                _order_id = order["AmazonOrderId"]

                self._expanded_orders.append({
                    "Order_data": order,
                    "Order_item_data": self._get_all_items(order_id=_order_id)
                })

        return self._expanded_orders
