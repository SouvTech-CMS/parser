import json
import time
from datetime import datetime

from etsyv3 import EtsyAPI

from configs.env import ETSY_API_KEY
from constants.auth_files_paths import ACCESS_TOKEN_RESPONSE_FILE_PATH, AUTH_CODE_RESPONSE_FILE_PATH
from constants.etsy_oauth import etsy_auth, STATE
from schemes.access_token import AuthToken
from schemes.auth_code import AuthCode

AUTH_CODE_WAIT_TIME_IN_SECONDS = 15
AUTH_TOKEN_LIFE_TIME_IN_SECONDS = 3600


def _save_auth_token(auth_token: AuthToken):
    with open(ACCESS_TOKEN_RESPONSE_FILE_PATH, 'w') as f:
        json.dump(auth_token.model_dump(), f)


def _get_auth_code() -> AuthCode:
    with open(AUTH_CODE_RESPONSE_FILE_PATH) as f:
        auth_code_response = AuthCode(**json.load(f))

    auth_code_exists = auth_code_response.code.strip()
    if not auth_code_exists:
        auth_url, _ = etsy_auth.get_auth_code()
        # TODO: send auth_url to telegram
        print(f"Auth code is not found. Open {auth_url} to grant access.")
        time.sleep(AUTH_CODE_WAIT_TIME_IN_SECONDS)
        return _get_auth_code()
        # raise Exception(f"Auth code is not found. Open {auth_url} to grant access.")

    return auth_code_response


def _get_auth_token() -> AuthToken:
    with open(ACCESS_TOKEN_RESPONSE_FILE_PATH) as f:
        auth_token = AuthToken(**json.load(f))

    auth_token_exists = auth_token.access_token.strip() and auth_token.refresh_token.strip() and auth_token.expires_at != 0
    if not auth_token_exists:
        auth_code_response = _get_auth_code()
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
        _save_auth_token(auth_token)

    return auth_token


def refresh_auth_token(etsy_api: EtsyAPI):
    new_access_token, new_refresh_token, new_expires_at = etsy_api.refresh()
    new_auth_token = AuthToken(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_at=new_expires_at.timestamp(),
    )
    _save_auth_token(new_auth_token)


def get_etsy_api():
    auth_token = _get_auth_token()

    etsy_api = EtsyAPI(
        keystring=ETSY_API_KEY,
        token=auth_token.access_token,
        refresh_token=auth_token.refresh_token,
        expiry=datetime.fromtimestamp(auth_token.expires_at),
    )

    now_timestamp = datetime.utcnow().timestamp()
    if now_timestamp > auth_token.expires_at:
        refresh_auth_token(etsy_api)
        return get_etsy_api()

    return etsy_api
