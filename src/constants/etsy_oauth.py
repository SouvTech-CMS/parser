from etsyv3.util.auth.auth_helper import AuthHelper

from configs.env import ETSY_API_KEY, ETSY_API_REDIRECT_URL, CODE_VERIFIER

ETSY_OAUTH_CONNECT_URL = "https://www.etsy.com/oauth/connect"
ETSY_OAUTH_TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"

SCOPES = [
    "listings_r",
    "transactions_r"
]

STATE = "superstate"

etsy_auth = AuthHelper(
    keystring=ETSY_API_KEY,
    redirect_uri=ETSY_API_REDIRECT_URL,
    scopes=SCOPES,
    code_verifier=CODE_VERIFIER,
    state=STATE,
)
