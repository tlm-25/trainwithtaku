#custom modules 
from src.database.connection import create_or_get_collection, create_or_get_database
from src.database.user_management.sign_up_form import  validate_input_form
from src.database.user_management.password import hash_password,is_correct_password 
from src.database.user_management.utils import check_if_email_already_in_use
from src.chatbot.chat_history import get_all_stored_user_chats, get_specific_stored_user_chat
from src.chatbot.chat_response import stream_chatbot_response
from src.config import USER_ACCOUNTS_COLLECTION_NAME, CHAT_COLLECTION_NAME, TEST_CHAT_COLLECTION_NAME,VECTOR_STORE_COLLECTION_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from src.schemas import UserSignUpForm, UserLoginForm, UserEmail,ClientForm, ChatRequest, Conversation, ChatHistoryRequest, ChatMessage
from src.database.user_management.jwt_token import create_access_token, get_user_by_email, get_current_user
import bcrypt
from pydantic import ValidationError
#mongo db
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, Response, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jwt.exceptions import InvalidTokenError

#Context management
from contextlib import asynccontextmanager
import uuid
import logging
from datetime import datetime
#configuration for logging file


app = FastAPI()

app.add_middleware(
    CORSMiddleware,

    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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
        
        #if confirm password and password fields do not match
        if "do not match" in form_submit_message.lower():
            error_code = 400
        else:
            # 422 error code (unprocessable entity) - inputs not in correct format
            error_code = 422

        logging.info(f"Failed to sign up: {form_submit_message}")
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




@app.post("/login_with_access_token")
async def login_with_access_token(database:AsyncDatabase=Depends(create_or_get_database),form_data: OAuth2PasswordRequestForm = Depends())->JSONResponse:
    
    main_database = database
    user_collection = main_database[USER_ACCOUNTS_COLLECTION_NAME]
    #check if email address can be found
    check_if_user_exists = await check_if_email_already_in_use(email_input=form_data.username,collection=user_collection)

    # if user exists and password is correct
    if check_if_user_exists:
        #retriever user info and log them in
        user_info = await user_collection.find_one(filter={"email":form_data.username},projection={"_id":True,"user":True,"password":True})

        #check if (hashed) passwords match for the corresponding user
        is_password_correct = is_correct_password(password_string=form_data.password,hashed_password=user_info["password"])

        
        if is_password_correct:
            # create and return JWT token if authenticated sucessfully
            access_token = create_access_token(data={"sub":str(user_info["_id"])})
 
            return JSONResponse(content={"access_token":access_token,"token_type":"bearer","message":"successful login"}, status_code=200)
        else:
            return JSONResponse(content={"message":"Incorrect email or password"}, status_code=401)
        
    else:
        return JSONResponse(content={"message":"Incorrect email or password"}, status_code=401)







@app.post("/get_stored_user_chats")
async def get_stored_user_chats(user:dict=Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database)):

    try:
        '''
        Retrieve all stored conversations for a given user email from the database

        :param email: Retrieved user info
        :type email: dict
        :param database: MongoDB database instance
        :type database: pymongo.asynchronous.database.AsyncDatabase
        :return: List of conversations associated with the user
        :rtype: list[dict]
        '''
        main_database = database
        conversations_collection = main_database[CHAT_COLLECTION_NAME]
        user_email = user["email"]
        stored_chats = await get_all_stored_user_chats(email=user_email,conversations_collection=conversations_collection)
        return JSONResponse(content=stored_chats, status_code=200)
    except Exception as e:  
        message =   f"Failed to retrieve stored chats: {e}" 
        logging.error(message) 
        return JSONResponse(content={"message":message}, status_code=500)








@app.post("/get_chat_history")
async def get_chat_history(chat_request:ChatHistoryRequest,current_user:dict =Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database)):
    '''
        Retrieve stored conversation for a given user and conversation ID.

        :param request: Request body containing the conversation_id
        :type request: ChatHistoryRequest
        :param current_user: Authenticated user dict
        :type current_user: dict
        :param database: MongoDB database instance
        :type database: AsyncDatabase
        :return: Chat history for the conversation
        :rtype: JSONResponse
        '''
    
    try:
        
        main_database = database
        conversations_collection = main_database[CHAT_COLLECTION_NAME]
        current_user_email = current_user["email"]

        chat_history = await get_specific_stored_user_chat(current_user_email=current_user_email,conversation_id=chat_request.conversation_id,conversations_collection=conversations_collection)
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
    conversation_collection = main_database[CHAT_COLLECTION_NAME]

    user_message = chat_request.user_message
    user_query = user_message.message
 

    # TODO INSERT USER QUERY INTO CONVERSATION
    add_message_to_db = await conversation_collection.update_one(
            {"conversation_id": chat_request.conversation_id},
            {"$push": {"messages": user_message.model_dump()}},
            upsert=True
            )
    print("saved message to db")


    response = StreamingResponse(stream_chatbot_response(user_query=user_query,chat_history=chat_request.chat_history,vector_store_collection=vector_store_collection,client_form=chat_request.client_form,conversation_id=chat_request.conversation_id,conversation_collection=conversation_collection))

    return response


    
@app.post("/create_new_chat")
async def create_new_chat(user:dict = Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database))->JSONResponse:
        '''
        Create a new converstion
        
            :param: user: The current user creating the chat
            :type user: str

            :param: create_new_chat
            :type  database: AsyncDatabase
        '''
        #generate random string to represent the chat id
        conversation_id = str(uuid.uuid4())

        #default greeting message for the chatbot
        now_datetime_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        default_message = {"type":"bot","message":"Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.",'timestamp': now_datetime_string}


        new_chat = Conversation(conversation_id=conversation_id,messages=[default_message],email=user["email"])

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



@app.post("/clear_chat")
async def clear_chat(chat:ChatHistoryRequest,database:AsyncDatabase=Depends(create_or_get_database)):

    main_database = database

    conversation_collection = main_database[CHAT_COLLECTION_NAME]

    conversation_id = chat.conversation_id
    #default chatbot message
    default_message = [ChatMessage(message="Hello! I'm your refund assistant - How can I help?", type="bot",timestamp=str(datetime.now())).model_dump()]

    # clear the chat and replace with default message
    clear_all_messages_from_convo = await conversation_collection.update_one(
    {"conversation_id": conversation_id},
    {"$set": {"messages": default_message}})

          
    print("Successfully cleared chat")
    logging.info("Successfully cleared chat")

    return JSONResponse(content={"message":"successfully cleared chat"},status_code=200)

@app.delete("/delete_chat")
async def delete_chat(chat:ChatHistoryRequest,database:AsyncDatabase=Depends(create_or_get_database)):
    '''
        Delete chat from database
    
    '''
    main_database = database

    try:

        conversation_collection = main_database[CHAT_COLLECTION_NAME]
        conversation_id = chat.conversation_id
        delete_conversation = await conversation_collection.delete_one({"conversation_id":conversation_id})
        return JSONResponse(content={"message":"successfully deleted chat"},status_code=200)
    except Exception as e:
        JSONResponse(content={"message":"Failed to delete chat"},status_code=500)

    


   


@app.get("/me")
async def get_user(user = Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database)):
    '''
    Endpoint to verify that we can retrieve the current user from the JWT token
    '''
    if user is None:
        raise HTTPException(status_code=401,detail="Invalid authentication credentials")
    
    return JSONResponse(content={"user_email":user["email"]},status_code=200)




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
        

        

        
        




 