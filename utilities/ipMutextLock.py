from asyncio import locks
from threading import Lock


class IpMutexLock:
    """
        A class making sure that only allow one request from one ip at the same time
    """
    locks: dict[str, Lock]
    
    def __init__(self) -> None:
        self.locks = {}
        
    def acquire(self, ip: str) -> None:
        """
            Acquire the lock for the given ip
        Args:
            ip (str): the given ip
        """
        
        if ip not in self.locks:
            self.locks[ip] = Lock()
        
        # Get the latest lock created and acquire the lock
        lock = self.locks[ip]
        lock.acquire()
        return
    
    def release(self, ip: str) -> None:
        """
            Release the lock for the given ip
        Args:
            ip (str): release the lock for the given ip
        """
        if ip in self.locks:
            lock = self.locks[ip]
            lock.release()
            
            # Erase the lock if it isn't used anymore
            if not lock.locked():
                del self.locks[ip]
            
        return