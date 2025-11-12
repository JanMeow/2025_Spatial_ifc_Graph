from cache.model import Cache
from typing import Annotated, Any
from fastapi import Depends

# Create the singleton cache instance here
# =========================================================================================
"""
Will change to Redis in Production, now for simplificty
"""
_cache_instance = Cache()
# =========================================================================================
def get_cache() -> Cache:
    """Return the singleton cache instance"""
    return _cache_instance
def get_cache_value(key: str):
    """Get a specific value from cache"""
    return _cache_instance.results.get(key)
def set_cache(cache: Cache, key: str, data: Any):
    """Set cache value"""
    cache_result = cache.results
    if key not in cache_result:
        cache_result[key] = data
    return cache_result[key]
def cleanup_cache(cache: Cache):
    """Clean up cache if it gets too large"""
    if len(cache.results) > cache.max_cahce_size:
        # Remove oldest entries (simple FIFO approach)
        keys_to_remove = list(cache.results.keys())[:len(cache.results) - cache.max_cahce_size + 10]
        for key in keys_to_remove:
            del cache.results[key]
        print(f"Cleaned up cache, removed {len(keys_to_remove)} entries")
# =========================================================================================
#  Cache Dependency
# =========================================================================================
CacheDep = Annotated[Cache, Depends(get_cache)]