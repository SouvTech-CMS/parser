import time

from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options

from configs.cookies import COOKIES
from constants.urls import ETSY_URL, COMPLETED_ORDERS_URL
from parser.get_order_details_by_id import get_order_details_by_id

options = Options()
# options.add_argument("--headless")

print("Starting Chrome browser...")
browser = Chrome(options=options, keep_alive=True)

browser.get(ETSY_URL)

for cookie in COOKIES:
    browser.add_cookie({
        'name': cookie['name'],
        'value': cookie['value']
    })

browser.refresh()

time.sleep(2)

browser.get(COMPLETED_ORDERS_URL)

time.sleep(7)

get_order_details_by_id(browser, "3279040146")

# orders_ids = get_orders_ids(browser)
#
# for order_id in orders_ids:
#     get_order_details_by_id(browser, order_id)

print("Closing process successfuly...")
time.sleep(2)
browser.quit()
