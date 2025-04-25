import json
from datetime import datetime

from schemes.order import Order
from schemes.client import Client
from schemes.city import City
from schemes.order_item import GoodInOrder
from schemes.upload_order import OrderData
from utils.format_datetime import iso_to_simple


def _format_order(*,
                  order: dict, order_obj: Order):
    """earliest fill order_obj"""
    order_obj.buyer_paid = None
    order_obj.order_id = order["AmazonOrderId"]
    order_obj.status = order["OrderStatus"]  # TODO может отличаться от бэка
    order_obj.date = iso_to_simple(order["PurchaseDate"])
    order_obj.quantity = 0
    order_obj.tax = 0


def _format_good_in_order(*,
                          item: dict,
                          item_obj: GoodInOrder):
    """fill good_in_order obj"""
    item_obj.uniquename = item["SellerSKU"]
    item_obj.quantity = item["QuantityOrdered"]
    if item.get("ItemPrice") and item.get("PromotionDiscount"):
        item_obj.amount = (
            (float(item["ItemPrice"]["Amount"]) * item["QuantityOrdered"]) - float(item["PromotionDiscount"]["Amount"])
        )
    item_obj.engraving_info = item["Title"]  # TODO чё надо?


def _format_client(*,
                   order: dict,
                   client_obj: Client):
    buyer_info = order.get("BuyerInfo")
    if buyer_info:
        client_obj.email = buyer_info["BuyerEmail"]


def _format_city(*,
                 order: dict,
                 city_obj: City):
    shipping_address = order.get("ShippingAddress")
    if shipping_address:
        city_obj.name = shipping_address["City"]
        city_obj.state = shipping_address["StateOrRegion"]
        city_obj.country = shipping_address["CountryCode"]


def format_order_data(*,
                      order: dict,
                      items: list[dict]) -> OrderData:
    order_obj = Order()
    client_obj = Client()
    city_obj = City()
    order_items = []

    _format_order(order=order, order_obj=order_obj)
    _format_client(order=order, client_obj=client_obj)
    _format_city(order=order, city_obj=city_obj)

    for item in items:
        good_in_order = GoodInOrder()
        _format_good_in_order(item=item, item_obj=good_in_order)

        # calculate tax and quantity for order
        order_obj.quantity += good_in_order.quantity

        if item.get("ItemTax") and item.get("PromotionDiscountTax"):
            order_obj.tax += (
                (good_in_order.quantity * float(item["ItemTax"]["Amount"])) - float(item["PromotionDiscountTax"]["Amount"])
            )

        order_items.append(good_in_order)

    return OrderData(
        order=order_obj,
        client=client_obj,
        city=city_obj,
        order_items=order_items
    )
