def get_auth_cookies(shop_cookie: str):
    cookies = [{
        "name": "p",
        "value": "eyJnZHByX3RwIjoxLCJnZHByX3AiOjF9"
    }, {
        "name": "session-key-www",
        "value": shop_cookie
    }]
    return cookies
