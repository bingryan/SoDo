import time
from functools import wraps
from twisted.internet.defer import DeferredLock


def rate_limited(max_per_second: int):
    """Rate-limits the decorated function locally, for one process."""
    lock = DeferredLock()
    min_interval = 1.0 / max_per_second

    def decorate(func):
        last_time_called = time.perf_counter()

        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            lock.acquire()
            nonlocal last_time_called
            try:
                elapsed = time.perf_counter() - last_time_called
                left_to_wait = min_interval - elapsed
                if left_to_wait > 0:
                    time.sleep(left_to_wait)

                return func(*args, **kwargs)
            finally:
                last_time_called = time.perf_counter()
                lock.release()

        return rate_limited_function

    return decorate


def size_limited(max_size: int):
    """size-limits the decorated function global"""
    lock = DeferredLock()
    max_limited_size = max_size

    def decorate(func):
        @wraps(func)
        def size_limited_function(*args, **kwargs):
            lock.acquire()
            nonlocal max_limited_size
            try:
                if max_limited_size > 0:
                    max_limited_size -= 1
                    return func(*args, **kwargs)
            finally:
                lock.release()

        return size_limited_function

    return decorate
