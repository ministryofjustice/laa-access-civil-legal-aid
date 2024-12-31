from flask_caching import Cache

cache_config = {
    "CACHE_TYPE": "SimpleCache",  # Stores the cache in application memory, later we should store this in elsewhere
    "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes
}
cache = Cache(config=cache_config)
