#custom modules 
from src.database.connection import create_or_get_collection, create_or_get_database
from src.database.user_management.sign_up_form import  validate_input_form
from src.database.user_management.password import hash_password,is_correct_password 
from src.database.user_management.utils import check_if_email_already_in_use
from src.chatbot.chat_history import get_all_stored_user_chats, get_specific_stored_user_chat
from src.chatbot.chat_response import stream_chatbot_response
from src.config import USER_ACCOUNTS_COLLECTION_NAME, CHAT_COLLECTION_NAME, TEST_CHAT_COLLECTION_NAME,VECTOR_STORE_COLLECTION_NAME
from src.schemas import UserSignUpForm, UserLoginForm, UserEmail,ClientForm, ChatRequest, Conversation
import bcrypt

#mongo db
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse, Response, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware



#Context management
from contextlib import asynccontextmanager
import uuid
import logging
from datetime import datetime
#configuration for logging file


app = FastAPI()



#create user 
@app.post("/add_user")
async def add_user(user_sign_up_form:UserSignUpForm,database:AsyncDatabase=Depends(create_or_get_database))->JSONResponse:
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

        #if user already exists
        if "already in use" in form_submit_message.lower():
            #  409 error code (request conflict, with current state of resource)
            error_code = 409
        else:
            # 422 error code (unprocessable entity) - inputs not in correct format
            error_code = 422

            
        return JSONResponse(content={"message":f"Failed to sign up: {form_submit_message}"},status_code=error_code)


    # if the input fields are all valid
    else: 
        # if email already in use for another account, alert the user 

        #hash password input for extra security 
        hashed_password = hash_password(password_string=password_input)

        #otherwise, add the new user to the database (username, hashed password, user_type)
        new_user = { "email": email_input,"password":hashed_password, "user_type": user_type_input }

        #TODO - function to send user confirmation email with passcode etc.?

        #insert new user to database
        inserted_documents = await users_collection.insert_one(document=new_user)
        
        return JSONResponse(content={"message":f"{form_submit_message}"},status_code=200)

#authenticate user
@app.post("/authenticate_user")
async def authenticate_user(user_login_form:UserLoginForm,database:AsyncDatabase=Depends(create_or_get_database)):
    '''
    User authentication - Check that the email and password are correct
    
    :param user_login_form: Information collected from the login form (email address and password )
    :type user_login_form: UserLoginForm
    '''

    incorrect_details_message = "Incorrect email or password. Please ensure they are spelt correctly. If you do not have an account, please create one first."
    successful_login_message = "successfully logged in"

    email_input = user_login_form.email
    password_input = user_login_form.password

    # collection with user account information
    main_database = database
    users_collection = main_database[USER_ACCOUNTS_COLLECTION_NAME]

    #check if email address can be found
    check_if_user_exists = await check_if_email_already_in_use(email_input=email_input,collection=users_collection)

    # if user exists and password is correct
    if check_if_user_exists:
        #retriever user info and log them in
        user_info = await users_collection.find_one(filter={"email":email_input},projection={"_id":False,"user":True,"password":True})

        #check if (hashed) passwords match for the corresponding user
        is_password_correct = is_correct_password(password_string=password_input,hashed_password=user_info["password"])
        if is_password_correct:
            
            return JSONResponse(content={"message":successful_login_message}, status_code=200)
        else:
            return JSONResponse(content={"message":incorrect_details_message}, status_code=401)
    else:

        return JSONResponse(content={"message":incorrect_details_message}, status_code=401)







@app.post("/get_stored_user_chats")
async def get_stored_user_chats(user_email:UserEmail,database:AsyncDatabase=Depends(create_or_get_database)):

    try:
        '''
        Retrieve all stored conversations for a given user email from the database

        :param email: User's email address
        :type email: str
        :param database: MongoDB database instance
        :type database: pymongo.asynchronous.database.AsyncDatabase
        :return: List of conversations associated with the user
        :rtype: list[dict]
        '''
        main_database = database
        conversations_collection = main_database[CHAT_COLLECTION_NAME]
        stored_chats = await get_all_stored_user_chats(email=user_email.email,conversations_collection=conversations_collection)
        return JSONResponse(content=stored_chats, status_code=200)
    except Exception as e:  
        message =   f"Failed to retrieve stored chats: {e}" 
        logging.error(message) 
        return JSONResponse(content={"message":message}, status_code=500)



@app.post("/get_chat_history/{conversation_id}")
async def get_chat_history(conversation_id:str,database:AsyncDatabase=Depends(create_or_get_database)):

    try:
        '''
        Retrieve all stored conversations for a given user email from the database

        :param email: User's email address
        :type email: str
        :param database: MongoDB database instance
        :type database: pymongo.asynchronous.database.AsyncDatabase
        :return: List of conversations associated with the user
        :rtype: list[dict]
        '''
        main_database = database
        conversations_collection = main_database[CHAT_COLLECTION_NAME]
        chat_history = await get_specific_stored_user_chat(conversation_id=conversation_id,conversations_collection=conversations_collection)
        return JSONResponse(content=chat_history, status_code=200)
    except Exception as e:  
        message =   f"Failed to retrieve stored chats: {e}" 
        logging.error(message) 
        return JSONResponse(content={"message":message}, status_code=500)

@app.post("/chat")
async def generate_chatbot_response(chat_request:ChatRequest,database:AsyncDatabase=Depends(create_or_get_database)):
    '''
    :param chat_request
    :type chat_request ChatRequest 
     
    '''
    main_database = database
    vector_store_collection = main_database[VECTOR_STORE_COLLECTION_NAME]

    response = StreamingResponse(stream_chatbot_response(user_query=chat_request.user_query,chat_history=chat_request.chat_history,vector_store_collection=vector_store_collection,client_form=chat_request.client_form))

    return response
    
@app.post("/create_new_chat/{email}")
async def create_new_chat(email:str,database:AsyncDatabase=Depends(create_or_get_database)):
        '''
        Create a new converstion
        
            :param: email: Email of the user creating the chat
            :type email: str

            :param: create_new_chat
            :type  database: AsyncDatabase
        '''
        #generate random string to represent the chat id
        conversation_id = str(uuid.uuid4())

        #default greeting message for the chatbot
        now_datetime_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        default_message = {"type":"bot","message":"Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.",'timestamp': now_datetime_string}


        new_chat = Conversation(conversation_id=conversation_id,messages=[default_message],email=email)

        new_chat_dict = new_chat.model_dump()

        conversations_collection = database[CHAT_COLLECTION_NAME]

        try:
            #insert new user to database
            inserted_conversation = await conversations_collection.insert_one(document=new_chat_dict)

            message = {"message":"successfully created new chat","conversation_id":conversation_id}
            logging.info(message)


            return JSONResponse(content=message,status_code=201)
        
        except Exception as e:

            message = {message:f"failed to create new chat: {e}",conversation_id:"n/a"}
            logging.info(message)


            return JSONResponse(content=message,status_code=409)




        

        

        
        




 