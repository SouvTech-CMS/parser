from schemes.order import Order
from schemes.client import Client
from schemes.city import City
from schemes.order_item import GoodInOrder
from schemes.upload_order import OrderData
from utils.format_datetime import iso_to_simple
from constants.status import OrderStatus


def _format_order(*,
                  order: dict, order_obj: Order):
    """earliest fill order_obj"""
    order_obj.buyer_paid = float(order.get("OrderTotal", {}).get("Amount", 0))
    order_obj.order_id = order.get("AmazonOrderId", "")
    order_obj.status = OrderStatus.get_backend_status(order.get("OrderStatus"))
    order_obj.date = iso_to_simple(order.get("PurchaseDate"))
    order_obj.quantity = 0
    order_obj.tax = 0


    #TODO на бэке сделать ручку под amazon


def _format_good_in_order(*,
                          item: dict,
                          item_obj: GoodInOrder):
    """fill good_in_order obj"""

    item_price = item.get("ItemPrice")
    item_quantity= item.get("QuantityOrdered")
    item_discount = item.get("PromotionDiscount")

    item_obj.uniquename = item.get("SellerSKU")
    item_obj.quantity = item_quantity

    _amount = 0.0
    if item_price and item_discount and item_quantity:
        _amount = (
            (float(item_price["Amount"]) * item_quantity) - float(item_discount["Amount"])
        )

    item_obj.amount = _amount
    item_obj.engraving_info = item["Title"]  # TODO СДЕЛАТЬ!!!!


def _format_client(*,
                   order: dict,
                   client_obj: Client):
    client_obj.email = order.get("BuyerInfo", {}).get("BuyerEmail")

def _format_city(*,
                 order: dict,
                 city_obj: City):
    shipping_address = order.get("ShippingAddress", {})
    city_obj.name = shipping_address.get("City")
    city_obj.state = shipping_address.get("StateOrRegion")
    city_obj.country = shipping_address.get("CountryCode")


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
        item_quantity = good_in_order.quantity
        item_tax = item.get("ItemTax")
        item_discount_tax = item.get("PromotionDiscountTax")

        order_obj.quantity += item_quantity

        _amount_tax = 0.0
        if item_tax and item_discount_tax and item_quantity:
            _amount_tax += (
                (item_quantity * float(item_tax["Amount"])) - float(item_discount_tax["Amount"])
            )
        order_obj.tax = _amount_tax

        order_items.append(good_in_order)

    return OrderData(
        order=order_obj,
        client=client_obj,
        city=city_obj,
        order_items=order_items
    )
