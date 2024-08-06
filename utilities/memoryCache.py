from threading import Lock
import time
from interfaces.cacheInterface import CacheInterface


class MemoryCache(CacheInterface):
    cache: dict
    duration: int
    
    def __init__(self, duration: int) -> None:
        self.cache = {}
        self.duration = duration
        
    def get(self, key):
        cache_entry = self.cache.get(key)
        
        if cache_entry is not None and time.time() - cache_entry['time_stamp'] < self.duration:
            return cache_entry['value']
        else:
            self.cache[key] = None
            return None
            
    def set(self, key, value):
        # Only allow one the edit at the time
        self.cache[key] = {
            'value': value,
            'time_stamp': time.time(),
        }
        