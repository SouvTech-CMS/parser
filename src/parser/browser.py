import time

from loguru import logger as log
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from constants.urls import ETSY_URL
from parser.auth_cookies import get_auth_cookies


def get_browser():
    options = Options()
    # options.add_argument("--headless")

    log.info("Starting Chrome browser...")
    browser = Chrome(options=options, keep_alive=True)
    browser.get(ETSY_URL)
    time.sleep(5)
    return browser


def update_browser_shop_cookies(browser: WebDriver, auth_cookie: str):
    auth_cookies = get_auth_cookies(auth_cookie)
    browser.delete_all_cookies()
    for cookie in auth_cookies:
        browser.add_cookie({
            "name": cookie['name'],
            "value": cookie['value'],
        })

    browser.refresh()
    return browser
