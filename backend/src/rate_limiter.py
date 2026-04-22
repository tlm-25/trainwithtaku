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


def create_rate_limiter(storage_uri: str | SecretStr | None = None) -> Limiter:
    '''
    Create a SlowAPI Limiter instance keyed by real client IP.

    Accepts a plain string (e.g. localhost dev URL), a Pydantic SecretStr
    (e.g. production credentials), or None for in-memory storage (e.g. tests).

    :param storage_uri: Redis connection string, or None for in-memory.
    :return: Configured Limiter instance.
    '''
    if storage_uri is None:
        return Limiter(key_func=get_real_ip)
    if isinstance(storage_uri, str):
        return Limiter(key_func=get_real_ip, storage_uri=storage_uri, in_memory_fallback_enabled=True)
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
    
    f"/send_change_password_link": f"Too many password reset requests. Please try again {retry_message}",
    
    "/reset_password": f"Too many password reset attempts. Please try again {retry_message}",
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


# TODO - handle load balancer and proxy ip so that limiter does not affect it 