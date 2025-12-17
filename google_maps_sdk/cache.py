"""
Simple TTL cache implementation (issue #37)
"""

import time
import hashlib
import json
from typing import Dict, Any, Optional, Tuple


class TTLCache:
    """
    Simple TTL (Time-To-Live) cache implementation
    
    Stores key-value pairs with expiration times.
    """
    
    def __init__(self, maxsize: int = 100, ttl: float = 300.0):
        """
        Initialize TTL cache
        
        Args:
            maxsize: Maximum number of items in cache
            ttl: Time-to-live in seconds (default: 300 = 5 minutes)
        """
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: Dict[str, Tuple[float, Any]] = {}  # key -> (expiry_time, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        if key not in self._cache:
            return False
        
        expiry_time, _ = self._cache[key]
        if time.time() > expiry_time:
            # Expired, remove it
            del self._cache[key]
            return False
        
        return True
    
    def __getitem__(self, key: str) -> Any:
        """Get value for key, raising KeyError if not found or expired"""
        if key not in self:
            raise KeyError(key)
        _, value = self._cache[key]
        return value
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set value for key with TTL"""
        # Remove expired entries if cache is full
        if len(self._cache) >= self.maxsize and key not in self._cache:
            self._evict_expired()
            # If still full, remove oldest entry
            if len(self._cache) >= self.maxsize:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
                del self._cache[oldest_key]
        
        expiry_time = time.time() + self.ttl
        self._cache[key] = (expiry_time, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value for key, returning default if not found or expired"""
        if key not in self:
            return default
        _, value = self._cache[key]
        return value
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def _evict_expired(self) -> None:
        """Remove all expired entries"""
        current_time = time.time()
        expired_keys = [k for k, (expiry, _) in self._cache.items() if current_time > expiry]
        for key in expired_keys:
            del self._cache[key]
    
    def __len__(self) -> int:
        """Return number of non-expired entries"""
        self._evict_expired()
        return len(self._cache)


def generate_cache_key(method: str, url: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate cache key from request parameters (issue #37)
    
    Args:
        method: HTTP method (GET, POST)
        url: Request URL
        params: Query parameters
        data: Request body data
        
    Returns:
        MD5 hash of request parameters as hex string
    """
    key_data = {
        "method": method,
        "url": url,
        "params": params or {},
        "data": data or {}
    }
    # Sort keys for consistent hashing
    key_json = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_json.encode()).hexdigest()
