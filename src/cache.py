from diskcache import Cache


class CacheManager:
    def __init__(self, cache_directory: str = ".app_cache"):
        self.cache = Cache(cache_directory, timeout=43200)

    def set(self, key: str, value: any, expire: int = None) -> None:
        """Store a value in the cache with the given key."""
        self.cache.set(key, value, expire=expire)

    def get(self, key: str) -> any:
        """Retrieve a value from the cache by key. Returns None if not found."""
        return self.cache.get(key)

    def clear(self) -> None:
        """Clear the entire cache."""
        self.cache.clear()
