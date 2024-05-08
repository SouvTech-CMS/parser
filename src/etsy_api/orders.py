import json

from configs.env import ETSY_SHOP_ID
from etsy_api.get_etsy_api import get_etsy_api


def get_all_orders_by_shop_id(shop_id: int):
    etsy_api = get_etsy_api()
    orders = etsy_api.get_shop_receipts(
        shop_id=shop_id,
        was_paid=None,
        was_shipped=None,
        limit=100,
        # offset=100,
    )
    return orders['results']


def get_shipping(
    shop_id: int,
    receipt_id: int | None,
    listing_id: int | None,
    shipping_profile_id: int | None,
):
    etsy_api = get_etsy_api()
    shipping = etsy_api.get_shop_shipping_profile(
        shop_id=shop_id,
        # min_created=1709583173,
        # max_created=1712261573,
        # receipt_id=receipt_id,
        # listing_id=listing_id,
        shipping_profile_id=shipping_profile_id,
        # origin_country_iso="US",
    )
    return shipping


if __name__ == "__main__":
    receipt_id = 3286094871
    listing_id = 1695473106
    shipping_profile_id = 227694839221
    ship = get_shipping(
        shop_id=ETSY_SHOP_ID,
        receipt_id=receipt_id,
        listing_id=listing_id,
        shipping_profile_id=shipping_profile_id,
    )
    # ship = get_all_orders_by_shop_id(ETSY_SHOP_ID)
    print(ship)

    with open("../../data/niko-ship.json", 'w') as f:
        json.dump(ship, f)

    # TODO: add shipping and ad parsing with selenium

    # orders = get_all_orders_by_shop_id(ETSY_SHOP_ID)
    # print(orders)
    #
    # orders_db: list[Order] = []
    # for order in orders:
    #     order_id = order['receipt_id']
    #
    #     order_created_at = datetime.fromtimestamp(order['created_timestamp'])
    #     day = order_created_at.day
    #     month = order_created_at.month
    #     year = order_created_at.year
    #
    #     formated_date = f"{day}.{month}.{year}"
    #
    #     quantity = 0
    #     for trans in order['transactions']:
    #         quantity += trans['quantity']
    #
    #     order_total = order['grandtotal']
    #     buyer_paid = order_total['amount'] / order_total['divisor']
    #     tax_total = order['total_tax_cost']
    #     tax_amount = tax_total['amount'] / tax_total['divisor']
    #     shipping_amount = ...
    #     purchased_after_ad = ...
    #
    #     orders.append(Order(
    #         shop_id=DB_SHOP_ID,
    #         order_id=order_id,
    #         date=formated_date,
    #         quantity=quantity,
    #         buyer_paid=buyer_paid,
    #         tax=tax_amount,
    #         shipping=shipping_amount,
    #         purchased_after_ad=purchased_after_ad,
    #     ))
