#custom modules 
from fastapi import FastAPI, Request
from fastapi.responses import  JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

#Context management
from contextlib import asynccontextmanager

import logging

#configuration for logging file

from src.routers import auth, chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,

    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        



