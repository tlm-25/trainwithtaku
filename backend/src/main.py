#custom modules 
from src.database.connection import create_or_get_database, get_mongo_client
from src.database.user_management.sign_up_form import validate_password_format, validate_email_format, check_if_passwords_match
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
    '''
        Add new user to the database 

        Arg(s):
            user_sign_up_form (UserSignUpForm) - Details of form that the user filled in 
    
    '''


    # user input fields - email, password, password confirmation ad 
    email_input = user_sign_up_form.email
    password_input = user_sign_up_form.password
    confirm_password_input = user_sign_up_form.confirm_password

    #list to store any error messages relating to incorrect formatting of the input fields
    input_format_error_messages = []


    
    #check that email does not already exist

    #check that email is valid format
    is_email_valid_format = validate_email_format(email_address=email_input)

    if not is_email_valid_format:
        input_format_error_messages.append("Email format not valid")
    
    

    #check that password is valid format
    is_password_valid_format = validate_password_format(password=password_input)

    if not is_password_valid_format:
        input_format_error_messages.append(f"Password it not valid format. It must contain lowercase and uppercase letters, at least 8 characters, at least one number and at least 1 special character")


    #check that password matches 
    password_fields_match_match = check_if_passwords_match(password=password_input,confirm_password=confirm_password_input)

    if not password_fields_match_match:
        input_format_error_messages.append(f"'Password' and 'Confirm Password' fields do not match")

    input_format_error_messages_string = " | ".join(input_format_error_messages)
    

    #check that all input fields are valid
    all_user_inputs_formats_valid = is_email_valid_format and is_password_valid_format and password_fields_match_match


    #if any of the input fields are invalid
    if not all_user_inputs_formats_valid:
        return JSONResponse(content={"message":f"Failed to sign up: {input_format_error_messages_string}"},status_code=422)

    # if the input fields are all valid
    else: 
        # if email already exists in database, alert the user 

        #otherwise, add the new user to the database (username, hashed password, user_type)
        pass







    
    


#authenticate user
@app.post("/authenticate_user")
async def authenticate_user(email:str,password:str):
    pass