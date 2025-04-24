import concurrent.futures
import json
import pprint
from datetime import datetime, timedelta

from api.parser import update_parser_status_by_id
from constants.status import ParserStatus
from etsy_api.orders import get_all_orders_by_shop_id
from schemes.upload_order import UploadingOrderData, OrderData
from utils.format_order_data import format_order_data
from utils.parser_shops_data import get_parser_shops_data
from utils.excel.write_each_row import write_to_excel
from configs import settings
from amazon_api.get_amazon_api import OrderClient



from sp_api.util import throttle_retry, load_all_pages

from configs import settings
from constants.amazon_credentials import CREDENTIALS_ARG
from constants.amazon_dates import LAST_MONTH_DATE, EARLIEST_DATE
from utils.safe_ratelimit_amazon import safe_rate_limit
from utils.format_datetime import is_iso_utc_z_format
from log.logger import logger



# Every 30 minutes
PARSER_WAIT_TIME_IN_SECONDS = 60 * 30
CREATED_AFTER = datetime(2024, 1, 1).isoformat().replace("+00:00", 'Z')

EXCEL_FILE = "data/check_point.xlsx" #temporaty


#TODO link on update refresh token don't forget!!!!

def process_single_shop(shop):

	# Initializing constants
	shop_error = False
	start_time_shop = datetime.now()
	order_cl = OrderClient(log=logger)

	offset = 0
	created_after = EARLIEST_DATE
	# weekday = datetime.now().weekday()
	##########################

	logger.info(f"Parsing shop {shop.shop_id} - {shop.shop_name}...")
	logger.info(
		f"Updating parser {shop.parser_id} status to {ParserStatus.PARSING}..."
	)

	update_parser_status_by_id(
		parser_id=shop.parser_id,
		status=ParserStatus.PARSING,
	)

	logger.success(f"Parser status updated.")


	uploading_orders = UploadingOrderData(shop_id=shop.shop_id, orders_data=[])


	#loop
	for page_orders in order_cl.load_all_orders(CreatedAfter=created_after):
		"""Every 100 orders after <CreatedAfter>"""

		logger.info(
			f"Fetching orders from {offset} to {offset + 100} from shop {shop.shop_name}..."
		)


		orders_data = order_cl.get_orders_with_items(page=page_orders)
		if orders_data is None:
			shop_error = True
			break

		#TODO подготовить upload
		uploading_orders.orders_data.append(
			OrderData(
				order=order,
				client=client,
				city=city,
				order_items=goods_in_order,
			)
		)

		# res = upload_orders_data(uploading_orders)
		with open("test_data.json", "w") as f:
			json.dump(uploading_orders.model_dump(), f)


		offset += 100

		if offset > 200:
			if now_hour == 20 and weekday in (5, 6):
				continue
			break

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


def etsy_api_parser():
	shops_data = get_parser_shops_data()

	# Используем ThreadPoolExecutor для параллельной обработки
	with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
		# Запускаем обработку каждого магазина в отдельном потоке
		futures = [executor.submit(process_single_shop, shop) for shop in shops_data]
		# Ждем завершения всех задач
		concurrent.futures.wait(futures)
		# Проверяем, были ли исключения
		for future in futures:
			if future.exception():
				logger.error(f"Error in thread: {future.exception()}")
	logger.success(f"Parsed all shops waiting {PARSER_WAIT_TIME_IN_SECONDS} to repeat")


if __name__ == "__main__":
	shops_data = get_parser_shops_data()
	process_single_shop(shops_data[2])
