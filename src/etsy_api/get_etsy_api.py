import json
import time
from datetime import datetime, timedelta

from etsyv3 import EtsyAPI
from loguru import logger as log
from typing_extensions import deprecated

from configs.env import ETSY_API_KEY
from constants.etsy_oauth import STATE, etsy_auth
from constants.files_paths import SHOPS_DATA_FILE_PATH
from schemes.access_token import AuthToken
from schemes.auth import AuthCode
from schemes.shop_data import ShopData

AUTH_CODE_WAIT_TIME_IN_SECONDS = 60
AUTH_TOKEN_LIFE_TIME_IN_SECONDS = 3600


class SouvTechEtsyAPI(EtsyAPI):
    shop_id: int

    def refresh(self) -> tuple[str, str, datetime]:
        log.info(f"Custom refreshing Etsy access token..")
        data = {
            "grant_type": "refresh_token",
            "client_id": self.keystring.split(":")[0],
            "refresh_token": self.refresh_token,
        }
        del self.session.headers["Authorization"]
        r = self.session.post("https://api.etsy.com/v3/public/oauth/token", data=data)
        log.info(f"Refresh token status code: {r.status_code}")
        refreshed = r.json()
        log.info(f"Refresh token response: {refreshed}")
        self.token = refreshed["access_token"]
        self.refresh_token = refreshed["refresh_token"]
        tmp_expiry = datetime.utcnow() + timedelta(seconds=refreshed["expires_in"])
        self.expiry = tmp_expiry
        self.session.headers["Authorization"] = "Bearer " + self.token
        if self.refresh_save is not None:
            self.refresh_save(self.token, self.refresh_token, self.expiry)

        # Update access token info in config
        log.success(f"New access token: {self.token}")
        log.success(f"New refresh token: {self.refresh_token}")
        log.success(f"New expiry: {self.expiry}")

        new_auth_token = AuthToken(
            access_token=self.token,
            refresh_token=self.refresh_token,
            expires_at=self.expiry.timestamp(),
        )
        _save_auth_token(new_auth_token, self.shop_id)
        #########

        return self.token, self.refresh_token, self.expiry


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
    with open(SHOPS_DATA_FILE_PATH, "w") as f:
        json.dump([shop_data.model_dump() for shop_data in shops_data], f)


def _get_auth_code(
    shop_id: int,
) -> AuthCode:
    shop_data = _get_shop_data_by_id(shop_id=shop_id)

    auth_code_exists = shop_data.shop_auth_code.strip()
    if not auth_code_exists:
        auth_url, _ = etsy_auth.get_auth_code()
        print(f"Auth code is not found. Open {auth_url} to grant access.")
        time.sleep(AUTH_CODE_WAIT_TIME_IN_SECONDS)
        return _get_auth_code(shop_id=shop_id)

    auth_code_response = AuthCode(code=shop_data.shop_auth_code)
    return auth_code_response


def _get_auth_token(
    shop_id: int,
    reset_auth_code: bool | None = False,
) -> AuthToken:
    shop_data = _get_shop_data_by_id(shop_id=shop_id)

    auth_token_exists = (
        shop_data.shop_token.strip()
        and shop_data.shop_refresh_token.strip()
        and shop_data.expiry != 0
    )
    if not auth_token_exists or reset_auth_code:
        auth_code_response = _get_auth_code(shop_id=shop_id)
        etsy_auth.set_authorisation_code(
            code=auth_code_response.code,
            state=STATE,
        )
        auth_token_response = etsy_auth.get_access_token()
        log.info(f"Auth token response: {auth_token_response}")
        auth_token = AuthToken(
            access_token=auth_token_response["access_token"],
            refresh_token=auth_token_response["refresh_token"],
            expires_at=auth_token_response["expires_at"],
        )
        _save_auth_token(
            auth_token=auth_token,
            shop_id=shop_id,
        )
        return _get_auth_token(
            shop_id=shop_id,
            reset_auth_code=reset_auth_code,
        )

    auth_token = AuthToken(
        access_token=shop_data.shop_token,
        refresh_token=shop_data.shop_refresh_token,
        expires_at=shop_data.expiry,
    )
    return auth_token


@deprecated("Token refresh inside EtsyAPI, not needed")
def refresh_auth_token(
    etsy_api: SouvTechEtsyAPI,
    shop_id: int,
):
    new_access_token, new_refresh_token, new_expires_at = etsy_api.refresh()
    log.success(f"New access token: {new_access_token}")
    log.success(f"New refresh token: {new_refresh_token}")
    log.success(f"New expiry: {new_expires_at}")
    new_auth_token = AuthToken(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_at=new_expires_at.timestamp(),
    )
    _save_auth_token(new_auth_token, shop_id)


def get_etsy_api(
    shop_id: int,
    reset_auth_code: bool | None = False,
) -> SouvTechEtsyAPI:
    auth_token = _get_auth_token(
        shop_id=shop_id,
        reset_auth_code=reset_auth_code,
    )

    etsy_api = SouvTechEtsyAPI(
        keystring=ETSY_API_KEY,
        token=auth_token.access_token,
        refresh_token=auth_token.refresh_token,
        expiry=datetime.fromtimestamp(auth_token.expires_at),
    )
    etsy_api.shop_id = shop_id
    time.sleep(3)

    # try:
    #     etsy_api.ping()
    # except Unauthorised:
    #     log.warning(f"Token is expired. Requesting new token.")
    #     return get_etsy_api(
    #         shop_id=shop_id,
    #         # reset_auth_code=True,
    #     )

    return etsy_api


if __name__ == "__main__":
    get_etsy_api(
        shop_id=2,
        reset_auth_code=True,
    )
