import functools
import time


def retry_with_backoff(max_attempts=3, base_delay=0.5, exceptions=(Exception,)):
    """Retry a function with exponential backoff on specific exception types.

    After max_attempts failures, re-raises the last exception rather than
    silently giving up or faking success.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts - 1:
                        break
                    time.sleep(base_delay * (2 ** attempt))
            raise last_exc

        return wrapper

    return decorator
