from etsy_api.get_etsy_api import get_etsy_api


def get_all_orders_by_shop_id(
    etsy_shop_id: int,
    shop_id: int,
    limit: int = 100,
    offset: int = 0,
):
    etsy_api = get_etsy_api(shop_id)
    orders = etsy_api.get_shop_receipts(
        shop_id=etsy_shop_id,
        was_paid=None,
        was_shipped=None,
        limit=limit,
        offset=offset,
    )
    return orders["results"], orders["count"]
