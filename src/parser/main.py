from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options

from configs.cookies import COOKIES
from constants.urls import ETSY_URL
from parser.get_order_details_by_id import get_order_shipping_by_id

if __name__ == "__main__":
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

    get_order_shipping_by_id(browser, "3279040146")

    # orders_ids = get_orders_ids(browser)
    #
    # for order_id in orders_ids:
    #     get_order_details_by_id(browser, order_id)

    print("Closing process successfully...")
    browser.quit()
