import json
import time
from datetime import datetime

from etsyv3 import EtsyAPI

from configs.env import ETSY_API_KEY
from constants.access_token import AuthToken
from constants.auth_code import AuthResponse, AUTH_RESPONSE_FILE_PATH
from constants.etsy_oauth import etsy_auth, STATE


def get_etsy_api():
    with open(AUTH_RESPONSE_FILE_PATH) as f:
        auth_response = AuthResponse(**json.load(f))
        etsy_auth.set_authorisation_code(
            code=auth_response.code,
            state=STATE
        )

    if not auth_response.code.strip():
        auth_url, _ = etsy_auth.get_auth_code()
        print(f"Auth code is not found. Open {auth_url} to grant access.")
        time.sleep(15)
        return get_etsy_api()
        # raise Exception(f"Auth code is not found. Open {auth_url} to grant access.")

    auth_token_response = etsy_auth.get_access_token()
    auth_token = AuthToken(
        access_token=auth_token_response['access_token'],
        refresh_token=auth_token_response['refresh_token'],
        expires_at=datetime.fromtimestamp(auth_token_response['expires_at']),
    )

    if not auth_token:
        raise Exception(f"Cannot get access token.")

    etsy_api = EtsyAPI(
        keystring=ETSY_API_KEY,
        token=auth_token.access_token,
        refresh_token=auth_token.refresh_token,
        expiry=auth_token.expires_at,
    )

    return etsy_api
