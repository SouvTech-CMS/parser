import json

from constants.files_paths import SHOPS_DATA_FILE_PATH
from schemes.shop_data import ShopData
from utils.json_file_handler import read_json

def get_parser_shops_data() -> list[ShopData]:
    shops_data_raw = read_json(SHOPS_DATA_FILE_PATH)
    return [ShopData(**shop_data) for shop_data in shops_data_raw]
