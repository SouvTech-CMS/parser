import json

from configs.env import DATA_FOLDER_PATH

with open(f"{DATA_FOLDER_PATH}/cookies.json") as f:
    COOKIES = json.load(f)
