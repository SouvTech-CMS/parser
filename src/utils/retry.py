from pprint import pprint

def retry(retry=10, exception_classes=None):
    if exception_classes is None:
        exception_classes = (Exception,)

    def decorator(function):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retry:
                try:
                    return function(*args, **kwargs)
                except exception_classes as e:
                    attempts += 1
                    if attempts >= retry:
                        raise e
                pprint(f"Retrying {function.__name__} (Attempt {attempts}/{retry}) due to error: {e}")

        wrapper.__doc__ = function.__doc__
        return wrapper

    return decorator
