from threading import Lock
import yaml
from interfaces.balancerInterface import BalancerInterface

MAX_INT = float('inf')

def load_server_configuration(path):
    with open(path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config['servers']

class RequestNumberBalancer(BalancerInterface):
    activeRequest: dict[str, int]
    mutexes: dict[str, Lock]
    servers: list[dict]
    
    def __init__(self) -> None:
        self.servers = load_server_configuration('config.yaml')
        self.activeRequest = {}
        self.mutexes = {}
        
        for server in self.servers:
            self.activeRequest[server['name']] = 0
            self.mutexes[server['name']] = Lock()
    
    def get_the_best_server(self) -> dict | None:
        """ Find the best server based on their current number of active requests
        Returns:
            dict | None: the best sever or None if all of the servers are unavailable
        """
        minimum = MAX_INT
        target_server = None
        
        for server in self.servers:
            # Start a mutext lock, only allow one thread to read at the same time
            self.mutexes[server['name']].acquire()
            try:
                num_current_request : int = self.activeRequest[server['name']]
                
                # If the server can handle one more request and it is the server with the lowest number of active request 
                # Then assign it to the current request
                if server['capacity'] > num_current_request  and num_current_request < minimum:
                    minimum = num_current_request
                    target_server = server
            finally:
                # Release the mutex lock
                self.mutexes[server['name']].release()
        
        return target_server 
    
    def active(self, server) -> None:
        """ Announce the balancer that start redirecting to the given server
        Args:
            server: the given server
        """
        # Start a mutex lock, only allow one thread to edit one value at the same time
        self.mutexes[server['name']].acquire()
        try:
            # Increase the current active requests for the given server by one
            self.activeRequest[server['name']] += 1
        finally:
            # Releas the mutext lock
            self.mutexes[server['name']].release()
            
    def release(self, server: dict) -> None:
        """ Announce the balancer that the request to the given server has ended
        Args:
            server (dict): the given server
        """
        # Start a mutex lock, only allow one thread to edit one value at the same time
        self.mutexes[server['name']].acquire()
        try:
            # Decrease the current active requests for the given server by one
            self.activeRequest[server['name']] -= 1
        finally:
            # Releas the mutext lock
            self.mutexes[server['name']].release()