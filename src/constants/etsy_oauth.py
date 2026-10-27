from etsyv3.util.auth.auth_helper import AuthHelper

from configs.env import ETSY_API_KEY, ETSY_API_REDIRECT_URL, CODE_VERIFIER
from etsy_api.request_timeout import set_etsy_request_timeout

ETSY_OAUTH_CONNECT_URL = "https://www.etsy.com/oauth/connect"
ETSY_OAUTH_TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"

SCOPES = [
    "listings_r",
    "transactions_r",
    "billing_r",
    "shops_r",
    "address_r",
    "profile_r",
    "feedback_r",
    "recommend_r",
]

STATE = "superstate"

etsy_auth = AuthHelper(
    keystring=ETSY_API_KEY,
    redirect_uri=ETSY_API_REDIRECT_URL,
    scopes=SCOPES,
    code_verifier=CODE_VERIFIER,
    state=STATE,
)
# NOTE: OAuth2Session is a requests.Session, used for auth code -> token exchange
set_etsy_request_timeout(etsy_auth.oauth)
