import time
from typing import Any


class SimpleCache:
    def __init__(self, ttl_seconds: int = 60):
        self._cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Any | None:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        self._cache[key] = (value, time.time())

    def clear(self):
        """Invalida todo el caché."""
        self._cache.clear()


# Global cache instances
team_cache = SimpleCache(ttl_seconds=300)  # 5 minutes
project_cache = SimpleCache(ttl_seconds=300)  # 5 minutes


def invalidate_all_caches():
    """Invalida todos los cachés globales."""
    team_cache.clear()
    project_cache.clear()
