import time

from selenium.webdriver.chrome.webdriver import WebDriver

from constants.urls import COMPLETED_ORDERS_URL, ETSY_URL


def check_auth_cookie(browser: WebDriver):
    browser.get(COMPLETED_ORDERS_URL)
    time.sleep(5)
    is_cookie_expired = browser.current_url.startswith(f"{ETSY_URL}/signin")
    return is_cookie_expired
