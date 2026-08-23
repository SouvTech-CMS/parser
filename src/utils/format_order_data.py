import contextlib
import json
from datetime import datetime

from schemes.city import City
from schemes.client import Client
from schemes.order import Order
from schemes.order_item import GoodInOrder


def format_order_data(
    order: dict,
) -> tuple[Order, list[GoodInOrder], Client, City]:
    order_id = order["receipt_id"]
    # Good in orders
    order_items = []
    order_created_at = datetime.fromtimestamp(order["created_timestamp"])
    ###########
    order_status = order["status"]
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
    with contextlib.suppress(Exception):
        city = City(
            name=order["city"],
            state=order["state"],
            country=order["country_iso"],
        )
    # Getting client info
    client = Client()
    with contextlib.suppress(Exception):
        client = Client(
            user_marketplace_id=str(order["buyer_user_id"]),
            name=order["name"],
            email=order["buyer_email"],
        )
    # Creating goods and good in order objects
    for trans in order["transactions"]:
        # Quantity of item
        quantity = trans["quantity"]
        # Full quantity of order items
        full_items_quantity += quantity
        # Name of good
        uniquename: str = trans["sku"]
        # Transaction ID
        listing_id: int = trans.get("listing_id")
        # Product ID
        product_id: int = trans.get("product_id")
        # Transaction Type
        transaction_type: str = trans.get("transaction_type")

        # Getting all additional engraving info
        engraving_info: dict = {}
        for variation in trans["variations"]:
            variation_name = variation.get("formatted_name")
            variation_value = variation.get("formatted_value")

            engraving_info_item: dict = {
                f"{variation_name}": f"{variation_value}",
                "listing_id": listing_id,
                "product_id": product_id,
                "transaction_type": transaction_type,
            }
            engraving_info.update(engraving_info_item)

        # Convert obj to str
        engraving_info_str = json.dumps(engraving_info)

        # Amount of item
        price = (trans["price"]["amount"] / trans["price"]["divisor"]) * quantity
        amount = price - trans["buyer_coupon"]
        #################
        order_items.append(
            GoodInOrder(
                uniquename=uniquename,
                quantity=quantity,
                amount=amount,
                engraving_info=engraving_info_str,
            )
        )

    order_total = order["grandtotal"]
    buyer_paid = order_total["amount"] / order_total["divisor"]
    tax_total = order["total_tax_cost"]
    tax_amount = tax_total["amount"] / tax_total["divisor"]

    shipping = (
        order["total_shipping_cost"]["amount"] / order["total_shipping_cost"]["divisor"]
    )

    order = Order(
        status=order_status,
        order_id=str(order_id),
        date=order_created_at,
        shipping=shipping,
        quantity=full_items_quantity,
        buyer_paid=buyer_paid,
        tax=tax_amount,
        receipt_shipping_id=receipt_shipping_id,
        tracking_code=tracking_code,
    )

    return order, order_items, client, city
