from slowapi import Limiter
from fastapi import Request
from pydantic import SecretStr
from fastapi import  Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from pydantic import SecretStr
from datetime import datetime
import logging
import jwt

from src.config import APP_CONFIG as config

JWT_SECRET_KEY = config.auth.jwt_secret_key.get_secret_value()
JWT_ALGORITHM = config.auth.jwt_algorithm.get_secret_value()

def get_real_ip(request: Request):
    '''
    Get the real IP address of the original client that made the request
    This is used when requests are forwarded via a load balancer or rate limiter

    :param request: The incoming request

    '''
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def get_user_id_from_token(request:Request) ->str:
    '''
    Get user id from the token 
    :param request: The incoming request
 
    '''
    
    # "Authorization" header has the JWT
    auth_header = request.headers.get("Authorization","")

    # assuming the user is logged in with JWT and the header with "Authorization": "Bearer <TOKEN>"

    if auth_header.startswith("Bearer"):

        jwt_token = auth_header[7:]

        payload =  jwt.decode(jwt=jwt_token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # return user id 
        return payload.get("sub")




def create_rate_limiter(storage_uri: str | SecretStr | None = None,key:str="ip") -> Limiter:
    '''
    Create a SlowAPI Limiter instance keyed by real client IP.

    Accepts a plain string (e.g. localhost dev URL), a Pydantic SecretStr
    (e.g. production credentials), or None for in-memory storage (e.g. tests).

    :param storage_uri: Redis connection string, or None for in-memory.
    :param key: Chosen key used to enforce rate limit. The options are 'ip' for ip address, and 'user' for user account
    :return: Configured Limiter instance.
    '''
    key_func_options = ["ip","user"]
    
    if not key.lower() in key_func_options:
        raise ValueError(f"'{key}' is not a valid key function. Please select from one of the following {key_func_options}")
    

    if storage_uri is None:
        return Limiter(key_func=get_real_ip)
    
    if key.lower() == "ip":
        return Limiter(key_func=get_real_ip, storage_uri=storage_uri, in_memory_fallback_enabled=True)
    
    elif key.lower() == "user":
        # rate limit by user id
        return Limiter(key_func=get_user_id_from_token, storage_uri=storage_uri, in_memory_fallback_enabled=True)
    return Limiter(key_func=get_real_ip, storage_uri=storage_uri.get_secret_value(), in_memory_fallback_enabled=True)


async def custom_rate_limit_handler(request:Request,exc:RateLimitExceeded):
    now = datetime.now().timestamp()
    # rate limit object from exception
    limit = exc.limit.limit

    # get the number of seconds in the time window
    window_seconds = limit.multiples * limit.GRANULARITY.seconds


    # get the tiemstamp of the reset 
    reset_timestamp = now + window_seconds

    if window_seconds < 60:
        retry_message = f"in {window_seconds} seconds"
    elif window_seconds < 3600:
        retry_message = f"in {window_seconds//60} minute(s)"
    else:
        retry_message = f"in {window_seconds//3600} hours"



    reset_time = datetime.fromtimestamp(reset_timestamp).strftime("%H:%M")

    logging.info(f" RL reset timestamp: {reset_time}")
    
    # time left before they can make requests again
    retry_after_s = int(reset_timestamp - now) if reset_timestamp else 60
   

    logging.info(f"Allowed to makes request again at {reset_time}")
    
    RATE_LIMIT_MESSAGES = {
    "/login_with_access_token": f"Too many login attempts. Please try again {retry_message} ",
    
    "/add_user": f"Too many sign up attempts. Please try again {retry_message}",
    
    "/send_change_password_link": f"Too many password reset requests. Please try again {retry_message}",
    
    "/reset_password": f"Too many password reset attempts. Please try again {retry_message}",
    
    "/chat": f"Max message allowance reached. Allowance resets {retry_message}"
    }

    rl_message = RATE_LIMIT_MESSAGES.get(request.url.path, "Too many requests. Please try again later")
    logging.info(f"Rate limit message: {rl_message}")
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": rl_message,
            "retry_after_seconds": window_seconds,
            "resets_at": reset_timestamp if reset_timestamp else None,
        },
        headers={
            "Retry-After": str(window_seconds),
            "X-RateLimit-Limit": str(exc.limit.limit.amount),
            "X-RateLimit-Remaining": str(retry_after_s),
            "X-RateLimit-Reset": str(int(reset_timestamp)) if reset_timestamp else "",
        },
    )


#TODO - Test for chat endpoint handling user based rate limiting

# TODO - handle load balancer and proxy ip so that limiter does not affect it 