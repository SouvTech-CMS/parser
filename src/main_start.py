from amazon_api.orders import get_all_orders
import json


if __name__ == "__main__":
    orders = get_all_orders()
    with open("check.json", 'W') as file:
        json.dump(orders, file, indent=4)
    print("ok")
    print(orders)