from datetime import datetime, timezone, timedelta

# WARNING: only ISO8601, endswith == Z

#first order was offer in 2024/2/17
EARLIEST_DATE = datetime(2024, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", 'Z')

#current date
CURRENT_DATE=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

#last month date
LAST_MONTH_DATE =  (datetime.now(timezone.utc) - timedelta(30)).isoformat().replace("+00:00", "Z")

#last week date
LAST_WEEK_DATE =  (datetime.now(timezone.utc) - timedelta(7)).isoformat().replace("+00:00", "Z")