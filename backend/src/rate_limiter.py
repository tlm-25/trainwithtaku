from slowapi import Limiter
from slowapi.util import get_remote_address
import redis
from fastapi import Request
import fastapi_limiter
from src.config import APP_CONFIG

REDIS_CONNECTION_STRING = APP_CONFIG.redis_config.redis_connection_string


def get_real_ip(request: Request):
    '''
    Get the real IP address of the original client that made the request 
    This is used when requests are forwarded via a load balancer or rate limiter

    :param request: The incoming request
    
    '''
    # if the request was forwarded via a proxy or load 
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, get the first one (this is client ip)
        # note that this is prone to spoofing, handle in ngnix
        return forwarded.split(",")[0].strip()
    return request.client.host



# instantiate rate limiter object - uses the ip address as the identifier for a request
# can use the identifier to know how many requests sent from the ip address
# slowapi limiter handles rate limiting under the hood - do not need to import redis class here (for now)
limiter = Limiter(key_func=get_real_ip,storage_uri=REDIS_CONNECTION_STRING.get_secret_value(),in_memory_fallback_enabled=True)

# maybe pass this as dependency , then create another function that gets the test limiter (to make it easier to test)
def get_limiter(storage_uri:str)->Limiter:
    limiter = Limiter(key_func=get_real_ip,storage_uri=storage_uri)
    return limiter



# TODO - handle load balancer and proxy ip so that limiter does not affect it 
