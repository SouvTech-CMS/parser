# NOTE: backend answers fast (uploading runs in background on its side),
# timeout guards from hanging when backend accepted connection but not responding
BACKEND_REQUEST_TIMEOUT_IN_SECONDS = 30
# NOTE: pause between failed attempts, so a down backend isn't hammered in a loop
BACKEND_RETRY_DELAY_IN_SECONDS = 30
UPLOAD_ORDERS_ATTEMPTS = 10
UPDATE_PARSER_STATUS_ATTEMPTS = 3
