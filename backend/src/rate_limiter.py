from slowapi import Limiter
from slowapi.util import get_remote_address
import redis


# instantiate rate limiter object - uses the ip address as the identifier for a request
# can use the identifier to know how many requests sent from the ip address

limiter = Limiter(key_func=get_remote_address)