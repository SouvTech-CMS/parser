import json
import time
from datetime import datetime

from etsyv3 import EtsyAPI

from configs.env import ETSY_API_KEY
from constants.etsy_oauth import etsy_auth, STATE
from constants.files_paths import SHOPS_DATA_FILE_PATH
from schemes.access_token import AuthToken
from schemes.auth import AuthCode
from schemes.shop_data import ShopData

AUTH_CODE_WAIT_TIME_IN_SECONDS = 15
AUTH_TOKEN_LIFE_TIME_IN_SECONDS = 3600


def _get_shop_data_by_id(shop_id: int) -> ShopData:
    with open(SHOPS_DATA_FILE_PATH) as f:
        shops_data = [ShopData(**shop) for shop in json.load(f)]
    for shop in shops_data:
        if shop.shop_id == shop_id:
            return shop


def _save_auth_token(auth_token: AuthToken, shop_id: int):
    with open(SHOPS_DATA_FILE_PATH) as f:
        shops_data = [ShopData(**shop_data) for shop_data in json.load(f)]
    for shop in shops_data:
        if shop.shop_id == shop_id:
            shop.shop_token = auth_token.access_token
            shop.shop_refresh_token = auth_token.refresh_token
            shop.expiry = auth_token.expires_at
    with open(SHOPS_DATA_FILE_PATH, 'w') as f:
        json.dump([shop_data.model_dump() for shop_data in shops_data], f)


def _get_auth_code(shop_id: int) -> AuthCode:
    shop_data = _get_shop_data_by_id(shop_id)

    auth_code_exists = shop_data.shop_auth_code.strip()
    if not auth_code_exists:
        auth_url, _ = etsy_auth.get_auth_code()
        print(f"Auth code is not found. Open {auth_url} to grant access.")
        time.sleep(AUTH_CODE_WAIT_TIME_IN_SECONDS)
        return _get_auth_code(shop_id)

    auth_code_response = AuthCode(code=shop_data.shop_auth_code)
    return auth_code_response


def _get_auth_token(shop_id: int) -> AuthToken:
    shop_data = _get_shop_data_by_id(shop_id)

    auth_token_exists = shop_data.shop_token.strip() and shop_data.shop_refresh_token.strip() and shop_data.expiry != 0
    if not auth_token_exists:
        auth_code_response = _get_auth_code(shop_id)
        etsy_auth.set_authorisation_code(
            code=auth_code_response.code,
            state=STATE,
        )
        auth_token_response = etsy_auth.get_access_token()
        auth_token = AuthToken(
            access_token=auth_token_response['access_token'],
            refresh_token=auth_token_response['refresh_token'],
            expires_at=auth_token_response['expires_at'],
        )
        _save_auth_token(auth_token, shop_id)
        return _get_auth_token(shop_id)

    auth_token = AuthToken(
        access_token=shop_data.shop_token,
        refresh_token=shop_data.shop_refresh_token,
        expires_at=shop_data.expiry,
    )
    return auth_token


def refresh_auth_token(etsy_api: EtsyAPI, shop_id: int):
    new_access_token, new_refresh_token, new_expires_at = etsy_api.refresh()
    print(f"new_access_token: {new_access_token}")
    print(f"new_refresh_token: {new_refresh_token}")
    print(f"new_expires_at: {new_expires_at}")
    new_auth_token = AuthToken(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_at=new_expires_at.timestamp(),
    )
    _save_auth_token(new_auth_token, shop_id)


def get_etsy_api(shop_id: int):
    auth_token = _get_auth_token(shop_id)

    etsy_api = EtsyAPI(
        keystring=ETSY_API_KEY,
        token=auth_token.access_token,
        refresh_token=auth_token.refresh_token,
        expiry=datetime.fromtimestamp(auth_token.expires_at),
    )

    now_timestamp = datetime.utcnow().timestamp()
    if now_timestamp > auth_token.expires_at:
        refresh_auth_token(etsy_api, shop_id)
        return get_etsy_api(shop_id)

    return etsy_api


get_etsy_api(1)
