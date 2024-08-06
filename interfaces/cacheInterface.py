class CacheInterface:
    def get(self, key):
        """
            Get the current value of the given key
        Args:
            key (Any): the given key
        """
        pass
    
    def set(self, key, value) -> None:
        """
            Set the value of the key with the given key
        Args:
            key (Any): the given key
            value (Any): the current value
        """
        pass