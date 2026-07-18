from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from pydantic import SecretStr
from fastapi.middleware.cors import CORSMiddleware
from src.routers.auth import create_auth_router
from src.routers.chat import create_chat_router
from src.routers.blog import upload_blog_router
from src.rate_limiter import create_rate_limiter, custom_rate_limit_handler


from pymongo.errors import ServerSelectionTimeoutError
import logging
from src.config import APP_CONFIG

frontend_dev_url = APP_CONFIG.domain.frontend_domain_dev
frontend_main_url = APP_CONFIG.domain.frontend_domain_main
ALLOWED_ORIGINS = ["http://localhost:5173","http://localhost:3000",frontend_dev_url,frontend_main_url]


def _custom_mongo_server_timeout_error(request:Request,exc:ServerSelectionTimeoutError)->JSONResponse:
    '''
    Handler for Mongo DB Server timeout errors 
    
    :param request: incoming request from client
    :param exc: The ServerSelectionTimeoutError raised when MongoDB is unreachable
     
    '''
    logging.error(f"Database connection failed: {exc}")


    return JSONResponse(
        content={"message": 
                 "Apologies, something is wrong on our end. We are looking to resolve this as soon as possible. Please try again later"},
        status_code=503
    )


def create_app(redis_rl_storage_uri:str|SecretStr|None=None)->FastAPI:
    '''
    Create FastAPI app instance with configured redis rate limiter 
    Redis rate limiter defaults to memory storate if uri not set.
    This function is synchronous, as there is not yet any io.
    However, the app it creates is async at runtime. 
    Using factory pattern to create fastapi app instance configured with 
    specific redis uri (makes testing rate limits easier)
    
    :param redis_rl_storage_uri: storage uri for redis database
    
    '''
    app = FastAPI()

    # rate limiter based on ip (default)
    ip_rate_limiter = create_rate_limiter(storage_uri=redis_rl_storage_uri)

    # rate limiter based on authenticated user 
    user_based_rate_limiter = create_rate_limiter(storage_uri=redis_rl_storage_uri,key="user")
    
    # app routers
    auth_router = create_auth_router(limiter=ip_rate_limiter)
    chat_router = create_chat_router(limiter=user_based_rate_limiter)
    blog_router = upload_blog_router()
    
    # find where these are needed in the app - defauly app.state.limiter read by slowapi _rate_limit_exceeded_handler 
    # however, using customer rate limit handler so this shouldn't be an issue 

    app.state.ip_rate_limiter = ip_rate_limiter
    app.state.user_based_rate_limiter = user_based_rate_limiter


    app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )
    # adding exception handlers to the app 
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
    app.add_exception_handler(ServerSelectionTimeoutError,_custom_mongo_server_timeout_error)
    app.include_router(auth_router,tags=["auth"])
    app.include_router(chat_router,tags=["chat"])
    app.include_router(blog_router,tags=["blog"])
    
    return app
