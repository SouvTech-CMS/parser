import requests as req
from loguru import logger as log

from api.auth import authorization
from configs.env import API_URL
from schemes.order_item import Good, GoodCreate


def check_good_in_base(product_id: str) -> Good | None:
    response = req.get(
        f"{API_URL}/good/by_product_id/{product_id}",
        headers=authorization().model_dump(),
    )
    if response.status_code != 200:
        return None
    data = response.json()
    return Good(
        id=data['id'],
        shop_id=data['shop_id'],
        product_id=data['product_id'],
        listing_id=data['listing_id'],
        price=data['price'],
        name=data['name'],
        description=data['description']
    )


def good_create(good: GoodCreate) -> Good | None:
    response = req.post(
        f"{API_URL}/good",
        headers=authorization().model_dump(),
        json=good.model_dump()
    )
    if response.status_code == 200:
        data = response.json()
        return Good(
            id=data['id'],
            shop_id=data['shop_id'],
            product_id=data['product_id'],
            listing_id=data['listing_id'],
            price=data['price'],
            name=data['name'],
            description=data['description'],
        )

    log.critical("Couldn't create good ")
    return None
