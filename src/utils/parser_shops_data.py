from configs import settings
from schemes.shop_data import ShopData

import json

def get_parser_shops_data() -> list[ShopData]:
    with open(settings.SHOPS_DATA_FILE_PATH) as f:
        shops_data = [ShopData(**shop_data) for shop_data in json.load(f)]

    return shops_data
