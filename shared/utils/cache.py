


import json
from functools import wraps


def cache_result(redis_client, key_prefix, expire_seconds=3600):
    """Decorator to cache function results in Redis."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{key_prefix}:{json.dumps(args)}:{json.dumps(kwargs)}"

            # Try to get from cache
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)

            # Calculate result
            result = func(*args, **kwargs)

            # Cache result
            redis_client.setex(
                key,
                expire_seconds,
                json.dumps(result)
            )

            return result

        return wrapper

    return decorator