from datetime import datetime
from loguru import logger as log
from schemes.city import City

from schemes.order import Order
from schemes.order_item import GoodInOrder
from schemes.client import Client


def format_order_data(
    order: dict,
):
    order_id = order["receipt_id"]
    # Good in orders
    order_items = []
    order_created_at = datetime.fromtimestamp(order["created_timestamp"])
    ###########
    day = order_created_at.day
    month = order_created_at.month
    year = order_created_at.year
    ###########
    order_status = order["status"]
    # Order date
    formated_date = f"{day}.{month}.{year}"
    # Full quantity of items in order
    full_items_quantity = 0

    # Getting order shipping info
    _shipping_info = order["shipments"]
    receipt_shipping_id = ""
    tracking_code = ""
    if len(_shipping_info):
        receipt_shipping_id = str(_shipping_info[0]["receipt_shipping_id"])
        tracking_code = str(_shipping_info[0]["tracking_code"])

    # Getting order city and state ordered from
    city = City()
    try:
        city = City(name=order["city"], state=order["state"])
    except Exception:
        pass
    # Getting client info
    client = Client()
    try:
        client = Client(
            user_marketplace_id=str(order["buyer_user_id"]),
            name=order["name"],
            email=order["buyer_email"]
        )
    except Exception:
        pass
    # Creating goods and good in order objects
    for trans in order["transactions"]:
        # Quantity of item
        quantity = trans["quantity"]
        # Full quantity of order items
        full_items_quantity += quantity
        # Name of good
        uniquename: str = trans["sku"]
        # Getting all aditional engraving info
        engraving_info: str = "["
        for variation in trans["variations"]:
            engraving_info += "{"
            engraving_info += "'{name}': '{value}'".format(
                name=variation["formatted_name"], value=variation["formatted_value"]
            )
            engraving_info += "}, "
        engraving_info = engraving_info.rstrip(", ") + "]"

        # Amount of item
        price = (trans["price"]["amount"] / trans["price"]["divisor"]) * quantity
        amount = price - trans["buyer_coupon"]
        #################
        order_items.append(
            GoodInOrder(
                uniquename=uniquename,
                quantity=quantity,
                amount=amount,
                engraving_info=engraving_info,
            )
        )

    order_total = order["grandtotal"]
    buyer_paid = order_total["amount"] / order_total["divisor"]
    tax_total = order["total_tax_cost"]
    tax_amount = tax_total["amount"] / tax_total["divisor"]
    order = Order(
        status=order_status,
        order_id=str(order_id),
        date=formated_date,
        quantity=full_items_quantity,
        buyer_paid=buyer_paid,
        tax=tax_amount,
        receipt_shipping_id=receipt_shipping_id,
        tracking_code=tracking_code,
    )

    return order, order_items, day, month, client, city
