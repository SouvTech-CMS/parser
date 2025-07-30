import json
from datetime import datetime

from api.parser import update_parser_status_by_id
from constants.status import ParserStatus
from schemes.shop_data import ShopData
from schemes.upload_order import UploadingOrderData
from utils.parser_shops_data import get_parser_shops_data
from amazon_api.get_amazon_api import OrderClient

from constants.amazon_dates import LAST_MONTH_DATE, EARLIEST_DATE
from log.logger import logger


def process_single_shop(shop: ShopData):

	order_cl = OrderClient(shop=shop)
	created_after = LAST_MONTH_DATE
	shop_error = False
	offset = 0
	start_time_shop = datetime.now()


	logger.info(f"Parsing shop {shop.shop_id} - {shop.shop_name}...")
	logger.info(
		f"Updating parser {shop.parser_id} status to {ParserStatus.PARSING}..."
	)

	update_parser_status_by_id(
		parser_id=shop.parser_id,
		status=ParserStatus.PARSING,
	)

	logger.success(f"Parser status updated.")

	for page_orders in order_cl.load_all_orders(CreatedAfter=created_after):
		"""Every 100 orders after <CreatedAfter>"""

		uploading_orders = UploadingOrderData(shop_id=shop.shop_id, orders_data=[])

		logger.info(
			f"Fetching orders from {offset} to {offset + 100} from shop {shop.shop_name}..."
		)

		orders_data = order_cl.get_orders_with_items(page=page_orders)
		if orders_data is None:
			shop_error = True
			break

		uploading_orders.orders_data.extend(orders_data)

		with open("test_data_2.json", "w") as f:
			json.dump(uploading_orders.model_dump(), f)

		offset += 100


	if shop_error:
		logger.error(f"Shop {shop.shop_id} - {shop.shop_name} parsed with error.")
		return
	logger.info(
		f"Updating parser {shop.parser_id} status to {ParserStatus.OK_AND_WAIT}..."
	)

	update_parser_status_by_id(
		parser_id=shop.parser_id,
		status=ParserStatus.OK_AND_WAIT,
		last_parsed=datetime.now().timestamp(),
	)

	logger.success(f"Parser status updated.")
	logger.success(f"Shop {shop.shop_id} - {shop.shop_name} parsed.")
	end_time_shop = datetime.now()
	logger.info(
		f"Shop  {shop.shop_id} - {shop.shop_name} parsing time: {end_time_shop - start_time_shop}"
	)


if __name__ == "__main__":
	shops_data = get_parser_shops_data()
	process_single_shop(shops_data[0])
