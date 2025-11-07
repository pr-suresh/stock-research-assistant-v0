"""
Caching utilities for the agent module.

Provides two-tier caching:
1. HTTP response cache (for API calls)
2. LLM response cache (for identical queries)
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


# ============================================================================
# In-Memory Cache (Phase 1 - Simple implementation)
# ============================================================================


class SimpleCache:
    """
    Simple in-memory cache with TTL support.

    This is a basic implementation for Phase 1. In production, consider:
    - Redis for distributed caching
    - LRU eviction policy
    - Persistent storage
    """

    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str, ttl: int = 300) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            Cached value or None if expired/missing
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < ttl:
                self._hits += 1
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                # Expired, remove it
                del self._cache[key]
                logger.debug(f"Cache expired: {key}")

        self._misses += 1
        logger.debug(f"Cache miss: {key}")
        return None

    def set(self, key: str, value: Any):
        """
        Store value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())
        logger.debug(f"Cache set: {key}")

    def clear(self):
        """Clear all cached values."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hits, misses, and hit rate
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "cached_entries": len(self._cache),
        }


# Global cache instance
_cache = SimpleCache()


def get_cache() -> SimpleCache:
    """Get the global cache instance."""
    return _cache


# ============================================================================
# Cache Key Generation
# ============================================================================


def generate_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate a deterministic cache key from parameters.

    Args:
        prefix: Key prefix (e.g., 'stock_price', 'query')
        **kwargs: Parameters to include in key

    Returns:
        SHA256 hash of the parameters
    """
    # Sort kwargs for consistent hashing
    sorted_params = json.dumps(kwargs, sort_keys=True)
    params_hash = hashlib.sha256(sorted_params.encode()).hexdigest()[:16]
    return f"{prefix}:{params_hash}"


# ============================================================================
# Cache Decorator
# ============================================================================


def cached(ttl: int = 300, key_prefix: Optional[str] = None):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds (default: 5 minutes)
        key_prefix: Custom prefix for cache key (default: function name)

    Example:
        @cached(ttl=60)
        def expensive_function(param):
            # ... expensive operation
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = generate_cache_key(
                prefix, args=args, kwargs=kwargs, func=func.__name__
            )

            # Try to get from cache
            cache = get_cache()
            cached_result = cache.get(cache_key, ttl=ttl)
            if cached_result is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_result

            # Cache miss - execute function
            logger.info(f"Cache miss for {func.__name__}, executing...")
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result)
            return result

        return wrapper

    return decorator


# ============================================================================
# HTTP Cache Setup (for Phase 2)
# ============================================================================


def setup_http_cache():
    """
    Set up HTTP response caching for API calls.

    Note:
        Full implementation coming in Phase 2 using requests-cache.
        Will cache yfinance API responses.
    """
    # TODO: Implement in Phase 2
    # import requests_cache
    # requests_cache.install_cache(
    #     'stock_research_cache',
    #     expire_after=300,
    #     allowable_codes=(200, 404),
    # )
    logger.info("HTTP cache setup (placeholder for Phase 2)")
