from slowapi import Limiter
from slowapi.util import get_remote_address
import redis
from src.config import APP_CONFIG

REDIS_CONNECTION_STRING = APP_CONFIG.redis_config.redis_connection_string

# instantiate rate limiter object - uses the ip address as the identifier for a request
# can use the identifier to know how many requests sent from the ip address
# slowapi limiter handles rate limiting under the hood - do not need to import redis class here (for now)
limiter = Limiter(key_func=get_remote_address,storage_uri=REDIS_CONNECTION_STRING)

# TODO - handle load balancer and proxy ip so that limiter does not affect it 