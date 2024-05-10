import time

from loguru import logger as log
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from constants.urls import COMPLETED_ORDERS_URL


def open_order_page_by_id(browser: WebDriver, order_id: str):
    browser.get(f"{COMPLETED_ORDERS_URL}?search_query={order_id}&order_id={order_id}")
    time.sleep(7)
    return browser


@log.catch(level="CRITICAL")
def get_order_shipping(browser: WebDriver):
    order_sidebar = browser.find_element(
        By.ID,
        "order-detail-container"
    )

    try:
        shipping_div = order_sidebar.find_element(
            By.CLASS_NAME,
            "wt-display-inline-flex-md.wt-display-inline-block"
        )
        # Total order shipping
        order_shipping = float(shipping_div.text[1:])
        return order_shipping
    # If order without shipping data
    except NoSuchElementException:
        return 0


@log.catch(level="CRITICAL")
def is_order_purchased_after_ad(browser: WebDriver):
    order_sidebar = browser.find_element(
        By.ID,
        "order-detail-container"
    )

    purchased_after_ad_icon = order_sidebar.find_elements(
        By.CLASS_NAME,
        "etsy-icon.icon-smaller.icon-b-4"
    )
    is_purchased_after_ad = len(purchased_after_ad_icon) == 1
    return is_purchased_after_ad

# if __name__ == "__main__":
#     browser = get_browser()
#     browser = update_browser_shop_cookies(browser,
#                                           "902020492-1262971206570-8aeb4dc8c2194f56ddeda9b0c278c6ba5ea4f85f972048f700f78923|1717821053")
#     browser = open_order_page_by_id(browser, "3297381056")
#     print(get_order_shipping(browser))

# def get_order_details_by_id(browser: WebDriver, order_id: str):
#     time.sleep(5)
#     browser.get(f"{COMPLETED_ORDERS_URL}?order_id={order_id}")
#     time.sleep(5)
#
#     order_sidebar = browser.find_element(
#         By.ID,
#         "order-detail-container"
#     )
#
#     order_status_and_data_div = order_sidebar.find_elements(
#         By.CLASS_NAME,
#         "mt-xs-1 show-xs show-sm"
#     )[0]
#
#     order_status_and_data_spans = order_status_and_data_div.find_elements(
#         By.TAG_NAME,
#         "span"
#     )
#
#     # Final order status
#     order_status = order_status_and_data_spans[0].find_element(
#         By.TAG_NAME,
#         "div"
#     ).find_element(
#         By.TAG_NAME,
#         "div"
#     ).text
#
#     # Final order date
#     order_date = order_status_and_data_spans[1].text
#
#     order_table = order_sidebar.find_element(
#         By.TAG_NAME,
#         "table"
#     )
#     order_trs = order_table.find_elements(
#         By.TAG_NAME,
#         "tr"
#     )[1:]
#
#     items_quantities = []
#     for tr in order_trs:
#         quantity_elem = tr.find_elements(
#             By.TAG_NAME,
#             "td"
#         )[1]
#         items_quantities.append(int(quantity_elem.text))
#
#     # Total order quantity
#     order_quantity = sum(items_quantities)
#
#     shipping_div = order_sidebar.find_elements(
#         By.CLASS_NAME,
#         "wt-display-inline-flex-md wt-display-inline-block"
#     )[0]
#     # Total order shipping
#     order_shipping = shipping_div.text
#
#     total_amount_and_tax_divs = order_sidebar.find_elements(
#         By.CLASS_NAME,
#         "col-xs-3 text-right pr-xs-0"
#     )[5:7]
#
#     # Total order tax
#     order_tax = total_amount_and_tax_divs[0].text
#
#     # Total order amount
#     order_total_amount = total_amount_and_tax_divs[1].text
#
#     print(f"12124:{order_id}")
#     print(f"12124:{order_status}")
#     print(f"12124:{order_date}")
#     print(f"12124:{order_quantity}")
#     print(f"12124:{order_shipping}")
#     print(f"12124:{order_tax}")
#     print(f"12124:{order_total_amount}")
