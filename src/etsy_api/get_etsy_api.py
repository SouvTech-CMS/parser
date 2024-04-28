import json
import time
from datetime import datetime

from etsyv3 import EtsyAPI

from configs.env import ETSY_API_KEY
from constants.access_token import AuthToken
from constants.auth_code import AuthCode, AUTH_CODE_RESPONSE_FILE_PATH, ACCESS_TOKEN_RESPONSE_FILE_PATH
from constants.etsy_oauth import etsy_auth, STATE

AUTH_CODE_WAIT_TIME_IN_SECONDS = 15


def _save_auth_token(auth_token: AuthToken):
    with open(ACCESS_TOKEN_RESPONSE_FILE_PATH, 'w') as f:
        # auth_token_data = auth_token.model_dump()
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


def get_etsy_api():
    auth_token = _get_auth_token()

    etsy_api = EtsyAPI(
        keystring=ETSY_API_KEY,
        token=auth_token.access_token,
        refresh_token=auth_token.refresh_token,
        expiry=datetime.fromtimestamp(auth_token.expires_at),
    )

    return etsy_api
