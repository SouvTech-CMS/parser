from pydantic import BaseModel


class ShopData(BaseModel):
    parser_id: int
    shop_id: int
    shop_name: str
    amazon_shop_id: str
