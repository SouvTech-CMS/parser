from amazon_api.get_amazon_api import OrderClient



def get_all_orders():
    order_client = OrderClient()
    orders = order_client.get_orders() # type: ignore

    return orders


