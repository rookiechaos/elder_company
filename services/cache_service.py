"""
Cache Service - In-memory caching for performance optimization
"""

import time
import hashlib
import json
from typing import Optional, Any, Dict, Callable
from functools import wraps
from threading import Lock
from datetime import datetime, timedelta


def get_cache_ttl() -> Dict[str, int]:
    """
    Get cache TTL values from settings.
    
    Returns:
        Dictionary mapping cache key prefixes to TTL values in seconds
    """
    from config.settings import settings
    return {
        "activity_templates": settings.cache_ttl_activity_templates,
        "user_config": settings.cache_ttl_user_config,
        "care_terms": settings.cache_ttl_care_terms,
        "customer_info": settings.cache_ttl_customer_info,
        "organization": settings.cache_ttl_organization,
        "translation": settings.cache_ttl_translation,
    }


class CacheService:
    """In-memory cache service with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments using SHA256.
        
        Uses SHA256 instead of hash() to avoid potential hash collisions
        and ensure consistent key generation across different Python runs.
        
        Args:
            prefix: Key prefix (typically function/module name)
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            SHA256 hash hexdigest (64 characters)
        """
        import json
        key_parts = [prefix]
        if args:
            # Serialize args to ensure consistent key generation
            key_parts.append(json.dumps(args, sort_keys=True, default=str))
        if kwargs:
            # Sort kwargs for consistent key generation
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(json.dumps(sorted_kwargs, sort_keys=True, default=str))
        
        key_string = ":".join(key_parts)
        # Use SHA256 for better collision resistance than MD5
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry["expires_at"] and time.time() > entry["expires_at"]:
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            self._stats["hits"] += 1
            return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL (in seconds)"""
        with self._lock:
            expires_at = None
            if ttl:
                expires_at = time.time() + ttl
            
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time()
            }
            self._stats["sets"] += 1
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries, optionally by pattern"""
        with self._lock:
            if pattern:
                keys_to_delete = [k for k in self._cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self._cache[key]
                return len(keys_to_delete)
            else:
                count = len(self._cache)
                self._cache.clear()
                return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self._stats,
                "size": len(self._cache),
                "hit_rate": round(hit_rate, 2)
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry["expires_at"] and entry["expires_at"] < current_time
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)


# Global cache instance
_cache_instance: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance


def cache_result(ttl: int = 3600, key_prefix: Optional[str] = None):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Optional prefix for cache key (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_result_async(ttl: int = 3600, key_prefix: Optional[str] = None):
    """
    Decorator to cache async function results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Cache TTL constants (in seconds)
CACHE_TTL = {
    "activity_templates": 3600,  # 1 hour
    "user_config": 1800,  # 30 minutes
    "care_terms": 86400,  # 24 hours
    "customer_info": 900,  # 15 minutes
    "organization": 1800,  # 30 minutes
    "translation": 300,  # 5 minutes (short TTL for dynamic content)
}
