from etsy_api.get_etsy_api import get_etsy_api


def get_all_orders_by_shop_id(shop_id: int):
    etsy_api = get_etsy_api()
    orders = etsy_api.get_listings_by_shop(shop_id)
    return orders


if __name__ == "__main__":
    shop_id = "fsgdg"
    orders = get_all_orders_by_shop_id(shop_id)
    print(orders)