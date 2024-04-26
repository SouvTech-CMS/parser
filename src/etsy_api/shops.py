from constants.shops import ShopName
from etsy_api.get_etsy_api import get_etsy_api


def find_shop_by_name(shop_name: str):
    etsy_api = get_etsy_api()
    shop = etsy_api.find_shops(shop_name)
    return shop


if __name__ == "__main__":
    shop = find_shop_by_name(ShopName.NIKO)
    print(shop)
