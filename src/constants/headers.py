from configs.env import ETSY_API_KEY

ETSY_API_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "x-api-key": ETSY_API_KEY,
}
