from collections import OrderedDict
import time

class CacheService:
    """In-memory LRU Cache for frequently requested queries and semantic retrievals."""
    
    def __init__(self, capacity=100, ttl_seconds=3600):
        self.capacity = capacity
        self.ttl = ttl_seconds
        self.cache = OrderedDict()

    def get(self, key):
        """Retrieve an item from the cache if it exists and hasn't expired."""
        if key not in self.cache:
            return None
            
        value, timestamp = self.cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return None
            
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        return value

    def set(self, key, value):
        """Add an item to the cache, evicting the oldest if at capacity."""
        if key in self.cache:
            self.cache.move_to_end(key)
            
        self.cache[key] = (value, time.time())
        
        # Evict LRU item if capacity is exceeded
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
            
    def clear(self):
        """Clear all items from the cache."""
        self.cache.clear()
