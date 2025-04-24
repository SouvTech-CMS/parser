from sp_api.base import ApiResponse
import time
from loguru import logger


def _delay_execution(*,
                     throttle_by_seconds: int,
                     header_limit: bool,
                     rate_limit: float) -> float:
    """delay in seconds"""
    if header_limit and rate_limit:
        return 1 / float(rate_limit)  # for dynamically rate limit
    return float(throttle_by_seconds)


def safe_rate_limit(throttle_by_seconds: int = 1,
                    header_limit: bool = False):
    def decorator(function):
        def wrapper(*args, **kwargs):
            resp: ApiResponse = function(*args, **kwargs)
            if not isinstance(resp, ApiResponse):
                return resp
            if resp.next_token:
                #excludes delay for several pages
                return resp
            logger.info(resp)
            logger.info(f"в декораторе и прошёл первичную проверку....")

            sleep_time = _delay_execution(throttle_by_seconds=throttle_by_seconds,
                                 header_limit=header_limit,
                                 rate_limit=resp.rate_limit)

            if sleep_time:
                logger.info(f"запуск слипа....{sleep_time}")
                time.sleep(sleep_time)
            return resp

        wrapper.__doc__ = function.__doc__
        return wrapper

    return decorator




