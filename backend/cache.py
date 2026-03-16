"""
cache.py — Tibby Chatbot Response Cache
Simple LRU cache with TTL, used to avoid redundant processing.
"""

from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Optional

from config import CACHE_MAX_SIZE, CACHE_TTL


class SimpleCache:
    """LRU cache with per-entry TTL for response caching."""

    def __init__(self, max_size: int = CACHE_MAX_SIZE, ttl: int = CACHE_TTL):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl

    def get(self, key: str) -> Optional[str]:
        """Return cached value if it exists and hasn't expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                self.cache.move_to_end(key)  # mark as recently used
                return value
            del self.cache[key]  # expired
        return None

    def set(self, key: str, value: str) -> None:
        """Store a value with the current timestamp."""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, datetime.now())
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)  # evict oldest

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self.cache.clear()


# Module-level singleton used across the app
response_cache = SimpleCache()
