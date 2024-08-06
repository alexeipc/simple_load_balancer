# Running command: flask --app loadbalancer run
from flask import Flask, Response, request, stream_with_context
import requests
from interfaces.balancerInterface import BalancerInterface
from interfaces.cacheInterface import CacheInterface
from utilities.ipMutextLock import IpMutexLock
from utilities.memoryCache import MemoryCache
from utilities.requestNumberBalancer import RequestNumberBalancer

RESPONSE_CHUNK_SIZE = 8192          # The size if 8192 bytes
CACHE_DURATION      = 10            # The duration gonna be 10 seconds     

# Declearing singleton
loadbalancer = Flask(__name__)
balancer : BalancerInterface = RequestNumberBalancer()          # Balance base on the number of active request of each server (this can be changed)
cache : CacheInterface = MemoryCache(CACHE_DURATION)            # Declare using memory cache (this can be changed)
ip_mutext_lock: IpMutexLock = IpMutexLock();

@loadbalancer.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@loadbalancer.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def route(path):
    """
        Get the route and pass it to the suitable server
    Returns:
        Response: The response for the request
    """
    
    # Get the client's ip and save in cache until expired
    client_ip = request.remote_addr
    cache_key = f'client_ip_{client_ip}'
    
    # Only allow one to read and edit the cache at the same time
    ip_mutext_lock.acquire(f'{client_ip}')
    try:
        # Try to retrive the data from cache
        cache_entry = cache.get(cache_key)
        if (cache_entry is None):
            target_server = balancer.get_the_best_server()
            
            cache.set(cache_key, target_server)
        else:
            target_server = cache_entry
    finally:
        # Release the lock for the ip
        ip_mutext_lock.release(f'{client_ip}')
    
    if (target_server == None):
        return 'Server is over loaded, please try again later'
    
    print(target_server)
    
    balancer.active(target_server)
    try:
        # Send the request to the target server with the given link:
        # f'http://{target_server['link']}/{path}
        
        url: str = f'http://{target_server['host']}/{path}'
        
        # Ignore the Host header
        headers = {key: value for key, value in request.headers if key != 'Host'} 
        
        response = requests.request(
            method=request.method,          # Use the method of the request  
            url=url,                        # The url
            headers=headers,                # Use the header of the request
            cookies=request.cookies,        # Use the cookies of the request
            data=request.get_data(),        # Use the data of the request
            stream=True                     # Enable streaming
        )
        
        # Create a generator to stream the response
        def generate():
            for chunk in response.iter_content(chunk_size=RESPONSE_CHUNK_SIZE):  # You can adjust chunk_size as needed
                yield chunk
        
        # Create a response
        flask_response = Response(response=stream_with_context(generate()), status=response.status_code, headers = dict(response.headers))
        
        # Paste the cookies
        for cookie in response.cookies:
            cookie_dict = cookie.__dict__.copy()
            cookie_dict['value'] = cookie_dict['value'] if cookie_dict['value'] is not None else ""
            flask_response.set_cookie(cookie.name, **cookie_dict)
        
        return flask_response
    finally:
        # Release the request for the balancer
        balancer.release(target_server)