# A simple load balancer using Python
## Set-up
- Install all the requirements:
```shell
pip install -r requirement.txt
```
- Config your servers from file `config.yaml`. Example:
```yaml
servers:
  - host: localhost:5081
    capacity: 100
    name: "The first server"
  - host: localhost:5231
    capacity: 100
    name: "The second server"
```
- Chunk size and cache duration can be change in file `loadbalancer.py`:
```python
RESPONSE_CHUNK_SIZE = 8192          # The size if 8192 bytes
CACHE_DURATION      = 10            # The duration gonna be 10 seconds     
```
- Load balancing algothim can be customized by creating a class extending `BalancerInterface.py` and be declared in `loadbalancer.py`. The default is least active request:
```python
balancer : BalancerInterface = RequestNumberBalancer()          # Balance base on the number of active request of each server (this can be changed)
```
- Caching service can be customized by creating a class extending `CacheInterface.py` and be declared in `loadbalancer.py`. The default is in-memory cache:
```python
cache : CacheInterface = MemoryCache(CACHE_DURATION)            # Declare using memory cache (this can be changed)
```

## Run
- Run the following comment to start the load balancer:
```shell
flask --app loadbalancer run
```
