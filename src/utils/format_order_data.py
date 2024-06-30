from datetime import datetime

from loguru import logger as log

from api.good import check_good_in_base, good_create
from schemes.order import Order
from schemes.order_item import GoodCreate, GoodInOrderCreate


def format_order_data(order: dict, shop_id: int, ):
    order_id = order['receipt_id']
    # Good in orders
    order_items = []
    order_created_at = datetime.fromtimestamp(order['created_timestamp'])
    ###########
    day = order_created_at.day
    month = order_created_at.month
    year = order_created_at.year
    ###########
    order_status = order['status']
    # Order date
    formated_date = f"{day}.{month}.{year}"
    # Full quantity of items in order
    quantity = 0
    # Creating goods and good in order objects
    for trans in order['transactions']:
        # Full quantity of order items
        quantity += trans['quantity']
        # Check is good in our base
        # Name of good
        uniquename = trans['sku']
        good = check_good_in_base(shop_id=shop_id, uniquename=uniquename)
        # Name For good if it not in our base
        if not good:
            # Creating new good object
            new_good = GoodCreate(
                shop_id=shop_id,
                uniquename=uniquename,
            )
            # Creating Good in our Base
            good = good_create(new_good)
            if not good:
                log.critical(f"Couldn't create a new good with uniquename {new_good.uniquename}")
                continue

        # Amount of item
        price = (trans['price']['amount'] / trans['price']['divisor']) * trans['quantity']
        amount = price - trans['buyer_coupon']
        #################

        order_items.append(
            GoodInOrderCreate(
                good_id=good.id,
                quantity=trans['quantity'],
                amount=amount,
            )
        )

    order_total = order['grandtotal']
    buyer_paid = order_total['amount'] / order_total['divisor']
    tax_total = order['total_tax_cost']
    tax_amount = tax_total['amount'] / tax_total['divisor']
    order = Order(
        status=order_status,
        shop_id=shop_id,
        order_id=str(order_id),
        date=formated_date,
        quantity=quantity,
        buyer_paid=buyer_paid,
        tax=tax_amount,
    )

    return order, order_items, day, month
