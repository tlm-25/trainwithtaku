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

from src.routers import auth, chat
from src.rate_limiter import limiter

app = FastAPI(title="Train with Taku API")

app.add_middleware(
    CORSMiddleware,

    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


app.include_router(auth.router,tags=["auth"])
app.include_router(chat.router,tags=["chat"])
        



