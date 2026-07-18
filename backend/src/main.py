#custom modules 
from fastapi import FastAPI, Request
from fastapi.responses import  JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

#Context management
from contextlib import asynccontextmanager

import logging

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.routers import auth, chat, blog
from src.config import APP_CONFIG
from src.app_setup import create_app

app = create_app(redis_rl_storage_uri=APP_CONFIG.redis_config.redis_connection_string)

# logging/printing any missing fields in pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    missing_fields = [
        err["loc"][-1]
        for err in exc.errors()
        if err["type"] == "value_error.missing"
    ]
    logging.info(missing_fields)

    return JSONResponse(
        status_code=422,
        content={
            "message": "Missing required fields",
            "missing_fields": missing_fields,
        },
    )




