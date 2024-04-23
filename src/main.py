import time

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from configs.cookies import COOKIES
from constants.urls import ETSY_URL, COMPLETED_ORDERS_URL
from get_orders_ids import get_orders_ids

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

orders_ids = get_orders_ids(browser)

for i in orders_ids:
    time.sleep(5)
    browser.get(f"{COMPLETED_ORDERS_URL}?order_id={i[1:]}")
    time.sleep(5)

    order_sidebar = browser.find_element(
        By.ID,
        "order-detail-container"
    )

    order_status_and_data_div = order_sidebar.find_elements(
        By.CLASS_NAME,
        "mt-xs-1 show-xs show-sm"
    )[0]
    order_status_and_data_spans = order_status_and_data_div.find_elements(
        By.TAG_NAME,
        "span"
    )

    # Final order status
    order_status = order_status_and_data_spans[0].find_element(
        By.TAG_NAME,
        "div"
    ).find_element(
        By.TAG_NAME,
        "div"
    ).text

    # Final order date
    order_date = order_status_and_data_spans[1].text

    order_table = order_sidebar.find_element(
        By.TAG_NAME,
        "table"
    )
    order_trs = order_table.find_elements(
        By.TAG_NAME,
        "tr"
    )[1:]

    items_quantities = []
    for tr in order_trs:
        quantity_elem = tr.find_elements(
            By.TAG_NAME,
            "td"
        )[1]
        items_quantities.append(int(quantity_elem.text))

    # Total order quantity
    order_quantity = sum(items_quantities)

    shipping_div = order_sidebar.find_elements(
        By.CLASS_NAME,
        "wt-display-inline-flex-md wt-display-inline-block"
    )[0]
    # Total order shipping
    order_shipping = shipping_div.text

    total_amount_and_tax_divs = order_sidebar.find_elements(
        By.CLASS_NAME,
        "col-xs-3 text-right pr-xs-0"
    )[5:7]

    # Total order tax
    order_tax = total_amount_and_tax_divs[0].text

    # Total order amount
    order_total_amount = total_amount_and_tax_divs[1].text

    print(f"12124:{i}")
    print(f"12124:{order_status}")
    print(f"12124:{order_date}")
    print(f"12124:{order_quantity}")
    print(f"12124:{order_shipping}")
    print(f"12124:{order_tax}")
    print(f"12124:{order_total_amount}")

print("Closing process successfuly...")
time.sleep(2)
browser.quit()
