from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


# TODO: get orders from all pages
def _get_orders_ids(browser: WebDriver):
    orders_ids_elems = browser.find_elements(
        By.TAG_NAME,
        "a"
    )

    orders_ids = []
    for elem in orders_ids_elems:
        a_text = elem.text.strip()
        if len(a_text) and a_text[0] == '#':
            orders_ids.append(a_text[1:])
    print(f"All orders ids: {orders_ids}")

    return orders_ids
