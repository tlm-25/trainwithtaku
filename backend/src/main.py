#custom modules 
from src.database.connection import create_or_get_collection, create_or_get_database
from src.database.user_management.sign_up_form import  validate_input_form
from src.database.user_management.password import hash_password,is_correct_password 
from src.database.user_management.utils import check_if_email_already_in_use
from src.chatbot.chat_history import get_all_stored_user_chats, get_specific_stored_user_chat
from src.chatbot.chat_response import stream_chatbot_response
from src.config import APP_CONFIG
USER_ACCOUNTS_COLLECTION_NAME = APP_CONFIG.database.user_accounts_collection_name
CHAT_COLLECTION_NAME = APP_CONFIG.database.chat_collection_name
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name
REFRESH_TOKEN_EXPIRE_DAYS = APP_CONFIG.auth.refresh_token_expire_days
from src.email_utils.sender import WELCOME_EMAIL_FILE_NAME, send_email

from src.schemas import UserSignUpForm, UserLoginForm, UserEmail,ClientForm, ChatRequest, Conversation, ChatHistoryRequest, ChatMessage


from src.database.user_management.jwt_token import (create_access_token, 
                                                    get_user_by_email, 
                                                    get_current_user, 
                                                    create_refresh_token, 
                                                    verify_token, 
                                                    blacklist_token,
                                                    hash_token,
                                                    is_correct_token)
import bcrypt
from pydantic import ValidationError
#mongo db
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection

from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, Response, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jwt.exceptions import InvalidTokenError

#Context management
from contextlib import asynccontextmanager
import uuid
import logging
from datetime import datetime, timezone
#configuration for logging file


app = FastAPI()

app.add_middleware(
    CORSMiddleware,

    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


EMAIL_CONFIG = APP_CONFIG.email

#create user 
@app.post("/add_user")
async def add_user(user_sign_up_form:UserSignUpForm,background_tasks:BackgroundTasks,database:AsyncDatabase=Depends(create_or_get_database))->JSONResponse:
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
        print(f"form_submit_message {form_submit_message}")

        #if user already exists
        if "already in use" in form_submit_message.lower():
            #  409 error code (request conflict, with current state of resource)
            error_code = 409
            
        
        #if confirm password and password fields do not match
        elif "do not match" in form_submit_message.lower():
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

        #TODO - function to send user confirmation welcome email after signing up

        #insert new user to database
        inserted_documents = await users_collection.insert_one(document=new_user)

        # make the email send a background task so that it doesn't bloxk the flow, and sign up can complete and let email send occur in the background
        background_tasks.add_task(send_email,recipients=[email_input],subject="Welcome!",context={"user":email_input},html_file_name=WELCOME_EMAIL_FILE_NAME)
        
        return JSONResponse(content={"message":f"{form_submit_message}"},status_code=200)




@app.post("/login_with_access_token")
async def login_with_access_token(database:AsyncDatabase=Depends(create_or_get_database),form_data: OAuth2PasswordRequestForm = Depends())->JSONResponse:
    '''
    This endpoint authenticates the user using username and password, sets the refresh token, stores it in the cookie, and returns an access token in the response body
    
    :param database: Database instance (MongoDB)
    :type database: AsyncDatabase
    :param form_data: User login details (username and password) from the login form
    :type form_data: OAuth2PasswordRequestForm
    
    
    '''


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
            access_token = await create_access_token(data={"sub":str(user_info["_id"])})

            # refresh token
            refresh_token = await create_refresh_token(data={"sub":str(user_info["_id"])})
            print(f"generated refresh token")
            


            # store hashed refresh token in database on login for specific user - to verify against when user tries to refresh access token or log out (invalidate refresh token)
            await user_collection.update_one({"_id":user_info["_id"]},{"$set":{"refresh_token":hash_token(token_string=refresh_token)}})




            max_age = REFRESH_TOKEN_EXPIRE_DAYS* 24 * 60 * 60 # length of validility of refresh token in seconds (for browser cookie)
            
            response = JSONResponse(content={"access_token":access_token,"token_type":"bearer","message":"successful login"}, status_code=200)
            # not sending refresh token to the client - setting to http only (stop javascript based attacks).
            # storing refresh token in browser cookie
            response.set_cookie(
                key="refresh_token",value=refresh_token, httponly=True, samesite="lax", max_age=max_age

            )
            print("cookie set on response")

 
            return response
        else:
            return JSONResponse(content={"message":"Incorrect email or password"}, status_code=401)
        
    else:
        return JSONResponse(content={"message":"Incorrect email or password"}, status_code=401)




@app.post("/refresh")
async def refresh_access_token(request:Request,database:AsyncDatabase=Depends(create_or_get_database)):
    '''
    Get a refresh token

    :param request: Request object containing information from browser cookie
    :type request: Request
    :param database: User and chatbot database
    :type databse: AsyncDatabase
 
    '''
    # get refresh token from cookie (assumes the user is logged in and has refresh token stored in browser cookie)
    refresh_token = request.cookies.get("refresh_token")


    # if no refresh token provided, return 401 error - user must be logged in to refresh the access token
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token is missing in browser cookie. Please log in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # check that refresh token is valid
    user = await verify_token(
        token=refresh_token,
        expected_token_type="refresh",
        database=database,
    )

    # check that the user associated with the refresh token exists in the database , and that the refresh token provided matches the (hashed) refresh token stored in database for that user (verify that the refresh token is valid and has not been rotated/invalidated by a new login or refresh)
    user_collection = database[USER_ACCOUNTS_COLLECTION_NAME]
    user_info = await user_collection.find_one({"_id": user["_id"]})
    stored_refresh_token_hashed = user_info.get("refresh_token")

    # token field removed from logout
    if not stored_refresh_token_hashed:
        raise HTTPException(status_code=401, detail="Refresh token has been rotated")


    if not is_correct_token(token_string=refresh_token,stored_hash=stored_refresh_token_hashed):
       
        # potential token theft — invalidate everything if old refresh token is being used by someone else after a new one has already been issued.  This is a security measure to protect users who may have had their refresh token stolen.
        await user_collection.update_one(
            {"_id": user["_id"]},
            #MongoDB syntex to remove refresh_token field
            {"$unset": {"refresh_token": ""}}
        )



        raise HTTPException(status_code=401, detail="Invalid refresh token")



    new_access_token = await create_access_token(data={"sub":str(user["_id"])})
    # new refresh token is generated and sent to user, and old refresh token is invalidated (by overwriting the hashed value in the database with the new one, so old refresh token can no longer be used to refresh access token or log out)
    new_refresh_token = await create_refresh_token(data={"sub": str(user["_id"])})  # brand new token

    # overwrite old hash in MongoDB
    await user_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"refresh_token": hash_token(new_refresh_token)}}
    )

    response = JSONResponse(
        content={"access_token":new_access_token,"token_type":"bearer"},
        status_code=200
    )

    # length of validility of refresh token in seconds (for browser cookie)
    max_age = REFRESH_TOKEN_EXPIRE_DAYS* 24 * 60 * 60 

    response.set_cookie(
        key="refresh_token",value=new_refresh_token, httponly=True, samesite
        ="lax", max_age=max_age)
    
    return response
    
    



@app.post("/get_stored_user_chats")
async def get_stored_user_chats(user:dict=Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database))->JSONResponse:
    '''
        Retrieve all stored conversations for a given user email from the database

        :param email: Retrieved user info
        :type email: dict
        :param database: MongoDB database instance
        :type database: pymongo.asynchronous.database.AsyncDatabase
        :return: List of conversations associated with the user
        :rtype: list[dict]
        '''

    try:
        
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
async def clear_chat(chat:ChatHistoryRequest,database:AsyncDatabase=Depends(create_or_get_database),user:dict=Depends(get_current_user)):

    
    
    try: 
        main_database = database

        conversation_collection = main_database[CHAT_COLLECTION_NAME]

        conversation_id = chat.conversation_id
        #default chatbot message
        default_message = [ChatMessage(message="Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.", type="bot",timestamp=str(datetime.now())).model_dump()]

        # clear the chat and replace with default message
        clear_all_messages_from_convo = await conversation_collection.update_one(
        {"conversation_id": conversation_id,"email":user["email"]},
        {"$set": {"messages": default_message}})

            
        print("Successfully cleared chat")
        logging.info("Successfully cleared chat")

        return JSONResponse(content={"message":"successfully cleared chat"},status_code=200)
    except Exception as e:
        return JSONResponse(content={"message":"Failed to delete chat"},status_code=500)


@app.delete("/delete_chat")
async def delete_chat(chat:ChatHistoryRequest,database:AsyncDatabase=Depends(create_or_get_database),user:dict = Depends(get_current_user)):
    '''
        Delete chat from database
    
    '''
    main_database = database

    try:

        conversation_collection = main_database[CHAT_COLLECTION_NAME]
        conversation_id = chat.conversation_id

        # delete conversation with matching conversation ID and user email (only allow deletion if chat belong to the user)
        delete_conversation = await conversation_collection.delete_one({"conversation_id":conversation_id,"email":user["email"]})
        return JSONResponse(content={"message":"successfully deleted chat"},status_code=200)
    except Exception as e:
        return JSONResponse(content={"message":"Failed to delete chat"},status_code=500)

    






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
        

        
@app.post("/logout")
async def logout(request:Request,database:AsyncDatabase=Depends(create_or_get_database)):
    """
    Invalidate the user's refresh token and clear the browser cookie. - Logs the user out
 
    The refresh token's JTI is written to the blacklist collection with its
    original expiry datetime.  The TTL index on that collection will
    automatically remove the blacklist entry once the token would have expired
    anyway, so the blacklist stays bounded.
 
    This endpoint deliberately does NOT require a valid access token — a user
    should always be able to log out, even if their access token has already
    expired.  The refresh token in the cookie is sufficient proof of identity
    for the purpose of invalidation.
 
    :param request: Incoming request (used to read the cookie).
    :type request: Request
    :param database: Async MongoDB database instance.
    :type database: AsyncDatabase
    :return: 200 on success; always clears the cookie regardless of token validity.
    :rtype: JSONResponse
    """
    refresh_token = request.cookies.get("refresh_token")  
    response = JSONResponse(content={"message": "successfully logged out"}, status_code=200)   
    # Always clear the cookie — even if the token is already invalid or missing.
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")
 
    if not refresh_token:
        return response
    
    # blacklisting the refresh token so it cannot be used again
 
    try:
        user = await verify_token(
            token=refresh_token,
            expected_token_type="refresh",
            database=database,
        )
        payload = user["_jwt_payload"]
        jti = payload.get("jti")
        exp = payload.get("exp")

        # JTI blacklist (catches reuse after logout)
 
        if jti and exp:
            expiry_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
            await blacklist_token(jti=jti, expiry=expiry_dt, database=database)
        

        #  remove stored hash (catches rotation theft)
        user_collection = database[USER_ACCOUNTS_COLLECTION_NAME]
        await user_collection.update_one(
            {"_id": user["_id"]},
            {"$unset": {"refresh_token": ""}}
        )
 
    except HTTPException:
        # Token is already invalid/expired — nothing to blacklist, still return 200.
        # handles smoothly in case where user logs out with already expired token, or if they try to log out twice in a row (second time there is no token)
        pass
 
    return response
  
        




 