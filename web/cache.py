#!/usr/bin/env python3
"""
Caching utilities for LOGDTW2002 web application
Provides in-memory caching for frequently accessed data
"""

from functools import wraps
from typing import Any, Callable, Optional
import time
from threading import Lock


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if expiry is None or time.time() < expiry:
                    self._hits += 1
                    return value
                else:
                    # Expired, remove it
                    del self._cache[key]
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache with optional TTL (time to live in seconds)"""
        with self._lock:
            expiry = time.time() + ttl if ttl else None
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """Delete a key from cache"""
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry is not None and now >= expiry
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "size": len(self._cache)
        }


# Global cache instance
cache = SimpleCache()


def cached(ttl: Optional[float] = None, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (None = no expiry)
        key_prefix: Prefix for cache keys
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from arguments"""
    return f"{str(args)}:{str(sorted(kwargs.items()))}"

