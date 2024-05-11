from etsy_api.get_etsy_api import get_etsy_api
from utils.parser_shops_data import get_parser_shops_data


def get_order(etsy_shop_id: int, shop_id: int, receipt_id: int):
    etsy_api = get_etsy_api(shop_id)
    orders = etsy_api.get_shop_receipt(
        shop_id=etsy_shop_id,
        receipt_id=receipt_id,
    )
    return orders


if __name__ == "__main__":
    shop_data = get_parser_shops_data()[1]
    order = get_order(
        etsy_shop_id=int(shop_data.etsy_shop_id),
        shop_id=shop_data.shop_id,
        receipt_id=3172066180,
    )
    print(order)
