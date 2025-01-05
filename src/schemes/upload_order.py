from pydantic import BaseModel
from schemes.order import Order
from schemes.client import Client
from schemes.city import City
from schemes.order_item import GoodInOrder


class OrderData(BaseModel):
    order: Order
    client: Client
    city: City
    order_items: list[GoodInOrder]


class UploadingOrderData(BaseModel):
    shop_id: int
    orders_data: list[OrderData]
