from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
#Context management
from contextlib import asynccontextmanager

app = FastAPI()