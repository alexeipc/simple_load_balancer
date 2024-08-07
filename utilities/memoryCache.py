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
        """ Return the value of the key if it has not been expired
        Args:
            key : the key we want to get

        Returns:
            The value if it exists in cache and has not been expired or else None
        """
        cache_entry = self.cache.get(key)
        
        if cache_entry is not None and time.time() - cache_entry['time_stamp'] < self.duration:
            return cache_entry['value']
        else:
            self.cache[key] = None
            return None
            
    def set(self, key, value):
        """ Get the key with the specific value
        Args:
            key: the given key
            value: the given value
        """
        self.cache[key] = {
            'value': value,
            'time_stamp': time.time(),
        }
        