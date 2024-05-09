import json

from constants.files_paths import SHOPS_DATA_FILE_PATH
from schemes.shop_data import ShopData


def get_parser_shops_data() -> list[ShopData]:
    with open(SHOPS_DATA_FILE_PATH) as f:
        shops_data = [ShopData(**shop_data) for shop_data in json.load(f)]

    return shops_data
