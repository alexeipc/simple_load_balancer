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
        # Start a mutex lock, only allow one thread to edit one value at the same time
        self.mutexes[server['name']].acquire()
        try:
            self.activeRequest[server['name']] += 1
        finally:
            # Releas the mutext lock
            self.mutexes[server['name']].release()
            
    def release(self, server: dict) -> None:
        # Start a mutex lock, only allow one thread to edit one value at the same time
        self.mutexes[server['name']].acquire()
        try:
            self.activeRequest[server['name']] -= 1
        finally:
            # Releas the mutext lock
            self.mutexes[server['name']].release()