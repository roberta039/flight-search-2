"""Cache manager for API responses and rate limiting."""
import time
from typing import Dict, Any, Optional
from cachetools import TTLCache
from datetime import datetime, timedelta

class CacheManager:
    """Manages caching and rate limiting for API calls"""
    
    def __init__(self):
        self.caches: Dict[str, TTLCache] = {}
        self.rate_limiters: Dict[str, list] = {}
    
    def get_cache(self, cache_name: str, ttl: int, maxsize: int = 100) -> TTLCache:
        """Get or create a cache with TTL"""
        if cache_name not in self.caches:
            self.caches[cache_name] = TTLCache(maxsize=maxsize, ttl=ttl)
        return self.caches[cache_name]
    
    def get_cached(self, cache_name: str, key: str, ttl: int = 300) -> Optional[Any]:
        """Retrieve cached data"""
        cache = self.get_cache(cache_name, ttl)
        return cache.get(key)
    
    def set_cached(self, cache_name: str, key: str, value: Any, ttl: int = 300):
        """Store data in cache"""
        cache = self.get_cache(cache_name, ttl)
        cache[key] = value
    
    def check_rate_limit(self, api_name: str, max_requests: int = 10, 
                        time_window: int = 60) -> bool:
        """Check if API call is within rate limit"""
        if api_name not in self.rate_limiters:
            self.rate_limiters[api_name] = []
        
        now = time.time()
        # Remove old timestamps
        self.rate_limiters[api_name] = [
            ts for ts in self.rate_limiters[api_name] 
            if now - ts < time_window
        ]
        
        # Check if under limit
        if len(self.rate_limiters[api_name]) < max_requests:
            self.rate_limiters[api_name].append(now)
            return True
        return False
    
    def wait_for_rate_limit(self, api_name: str, max_requests: int = 10, 
                           time_window: int = 60):
        """Wait until rate limit allows next request"""
        while not self.check_rate_limit(api_name, max_requests, time_window):
            time.sleep(1)
    
    def clear_cache(self, cache_name: Optional[str] = None):
        """Clear specific cache or all caches"""
        if cache_name:
            if cache_name in self.caches:
                self.caches[cache_name].clear()
        else:
            for cache in self.caches.values():
                cache.clear()

# Global cache manager instance
cache_manager = CacheManager()
