"""
Simple Cache Service for Performance Optimization (QA02)
Provides basic caching without Redis dependency
"""
from functools import wraps
import time

# Simple in-memory cache
_cache = {}
_cache_timestamps = {}

def get_cache_stats():
    """Get cache statistics for monitoring"""
    return {
        'enabled': True,
        'type': 'memory',
        'keys': len(_cache),
        'hits': 0,  # Could track this if needed
        'misses': 0
    }

def cache_get(key):
    """Get value from cache"""
    if key in _cache:
        # Check if expired (5 minutes TTL)
        if time.time() - _cache_timestamps.get(key, 0) < 300:
            return _cache[key]
        else:
            # Expired, remove
            del _cache[key]
            del _cache_timestamps[key]
    return None

def cache_set(key, value, ttl=300):
    """Set value in cache with TTL"""
    _cache[key] = value
    _cache_timestamps[key] = time.time()
    return True

def cache_delete(key):
    """Delete key from cache"""
    if key in _cache:
        del _cache[key]
        del _cache_timestamps[key]
        return True
    return False

def cache_clear():
    """Clear all cache"""
    _cache.clear()
    _cache_timestamps.clear()
    return True

def cached(ttl=300):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and args
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = cache_get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

def get_redis():
    """Compatibility function - returns None (no Redis)"""
    return None

def cache_delete_pattern(pattern):
    """Delete cache keys matching pattern"""
    count = 0
    keys_to_delete = [k for k in _cache.keys() if pattern in k]
    for key in keys_to_delete:
        cache_delete(key)
        count += 1
    return count
