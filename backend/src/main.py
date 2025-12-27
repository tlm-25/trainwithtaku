#custom modules 
from src.database.connection import create_or_get_collection, create_or_get_database
from src.database.user_management.sign_up_form import  validate_input_form
from src.database.user_management.password import hash_password,is_correct_password 
from src.config import USER_ACCOUNTS_COLLECTION_NAME
from src.schemas import UserSignUpForm
import bcrypt

#mongo db
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from fastapi import FastAPI, Depends
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
async def add_user(user_sign_up_form:UserSignUpForm,database:AsyncCollection=Depends(create_or_get_database))->JSONResponse:
    '''
        Add new user to the database 

        :param user_sign_up_form: user inputs from the 'sign up' form
        :type user_sign_up_form: UserSignUpForm - Details of form that the user filled in 
        :param user_collection:  Collection in database which stores user info
        :type user_collection: pymongo.asynchronous.collection.AsyncCollection
         
    '''
    main_database = database
    # user_accounts_collection = await create_or_get_collection(collection_name=USER_ACCOUNTS_COLLECTION_NAME)
    users_collection = main_database[USER_ACCOUNTS_COLLECTION_NAME]

    # user input fields - email, password, password confirmation and user type
    email_input = user_sign_up_form.email
    password_input = user_sign_up_form.password
    confirm_password_input = user_sign_up_form.confirm_password
    user_type_input = user_sign_up_form.user_type

    #check that all the forms are a valid format
    check_form_valid,form_submit_message = await validate_input_form(email_input=email_input,password_input=password_input,confirm_password_input=confirm_password_input,collection=users_collection)




    #if any of the input fields are invalid
    if not check_form_valid:
        return JSONResponse(content={"message":f"Failed to sign up: {form_submit_message}"},status_code=422)

    # if the input fields are all valid
    else: 
        # if email already in use for another account, alert the user 

        #hash password input for extra security 
        hashed_password = hash_password(password_string=password_input)

        #otherwise, add the new user to the database (username, hashed password, user_type)
        new_user = { "email": email_input,"password":hashed_password, "user_type": user_type_input }

        
        inserted_documents = await users_collection.insert_one(document=new_user)
        
        return JSONResponse(content={"message":f"{form_submit_message}"},status_code=200)




        







    
    


#authenticate user
@app.post("/authenticate_user")
async def authenticate_user(email:str,password:str):
    pass