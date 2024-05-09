from pydantic import BaseModel


class ShopData(BaseModel):
    parser_id: int
    shop_id: int
    shop_name: str
    shop_cookie: str
    shop_token: str
    shop_refresh_token: str
    expiry: float
    etsy_shop_id: str
    shop_auth_code: str
