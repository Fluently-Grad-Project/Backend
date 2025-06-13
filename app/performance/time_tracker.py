import functools
import logging
import time

logger = logging.getLogger(__name__)


def track_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        response = await func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{func.__name__} took {elapsed:.4f}s")
        return response

    return wrapper
