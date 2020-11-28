from functools import wraps
from typing import Callable
import time


def timer(fn: Callable):
    """Timer decorator"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        print('[timer] function={} timeTakenMillis={:.1f}'.format(fn.__name__, (end - start) * 1000))
        return result
    return wrapper
