"""Cache management utilities."""
import hashlib
import json
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Simple cache manager for predictions and news."""
    
    def __init__(self):
        self._cache = {}
        self._max_size = 1000
    
    def generate_key(self, data: Any) -> str:
        """Generate cache key from data."""
        if isinstance(data, str):
            return hashlib.md5(data.encode()).hexdigest()
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        if len(self._cache) >= self._max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = value
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)

# Global cache instance
prediction_cache = CacheManager()
