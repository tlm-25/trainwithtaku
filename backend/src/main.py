#custom modules 
from src.database.connection import create_or_get_database, get_mongo_client
from src.schemas import UserSignUpForm


#mongo db
from pymongo import AsyncMongoClient

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware



#Context management
from contextlib import asynccontextmanager


import logging
#configuration for logging file
logging.basicConfig(filename='src/log_files/chat_data.log', level=logging.DEBUG)


app = FastAPI()



#create user 
@app.post("/add_user")
async def add_user(user_sign_up_form:UserSignUpForm):
    # if not (username and email and password):
    #     message = {"message":"missing field"}
    #     return JSONResponse(content=message,status_code=422)

    #validate user fields

    # push user to database
    pass



#authenticate user
@app.post("/authenticate_user")
async def authenticate_user(username:str,email:str,password:str):
    pass