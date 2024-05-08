import requests

from configs.env import API_URL


def send_orders_data(data: any):
    response = requests.post(
        f"{API_URL}/...",
        json=data,
    )

    if response.status_code == 200:
        return response.json()

    return None
