from datetime import datetime

from schemes.order import Order


def format_order_data(order: dict, shop_id: int):
    order_id = order['receipt_id']

    order_created_at = datetime.fromtimestamp(order['created_timestamp'])
    day = order_created_at.day
    month = order_created_at.month
    year = order_created_at.year

    formated_date = f"{day}.{month}.{year}"

    quantity = 0
    for trans in order['transactions']:
        quantity += trans['quantity']

    order_total = order['grandtotal']
    buyer_paid = order_total['amount'] / order_total['divisor']
    tax_total = order['total_tax_cost']
    tax_amount = tax_total['amount'] / tax_total['divisor']

    order = Order(
        shop_id=shop_id,
        order_id=order_id,
        date=formated_date,
        quantity=quantity,
        buyer_paid=buyer_paid,
        tax=tax_amount,
    )
    return order
