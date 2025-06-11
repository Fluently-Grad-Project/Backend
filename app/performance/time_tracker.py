import time

from fastapi import logger

def track_time(endpoint_func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        response = await endpoint_func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{endpoint_func.__name__} took {elapsed:.4f}s")
        return response
    return wrapper
