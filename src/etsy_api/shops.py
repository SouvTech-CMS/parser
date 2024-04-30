from etsy_api.get_etsy_api import get_etsy_api


def find_shop_by_name(shop_name: str):
    etsy_api = get_etsy_api()
    shop = etsy_api.find_shops(shop_name)
    return shop


def get_shop_by_id(shop_id: int):
    etsy_api = get_etsy_api()
    shop = etsy_api.get_shop(shop_id)
    return shop


if __name__ == "__main__":
    # shop_name = ShopName.NIKO
    # shop = find_shop_by_name(shop_name)
    # print(shop)
    # with open(f"{shop_name}.json", 'w') as f:
    #     json.dump(shop, f)

    shop_id = 50508356
    shop = get_shop_by_id(shop_id)
    print(shop)
