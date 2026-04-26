#custom modules 
from src.database.connection import  create_or_get_database
from src.database.user_management.sign_up_form import  validate_input_form
from src.database.user_management.password import hash_password,is_correct_password 
from src.database.user_management.utils import check_if_email_already_in_use

from src.schemas import UserSignUpForm, UserEmail, UserResetPasswordForm

from src.database.user_management.sign_up_form import check_if_passwords_match,validate_password_format
from src.database.user_management.jwt_token import (create_access_token, 
                                                    get_current_user, 
                                                    create_refresh_token, 
                                                    verify_token, 
                                                    blacklist_token,
                                                    hash_token,
                                                    is_correct_token)


#mongo db
from pymongo.asynchronous.database import AsyncDatabase

from fastapi import Depends, HTTPException, Request, BackgroundTasks, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

#rate limiting
from src.rate_limiter import  create_rate_limiter
from slowapi import Limiter

#Context management
from contextlib import asynccontextmanager
import uuid
import logging
from datetime import datetime, timezone, timedelta


# config
from src.config import APP_CONFIG
from pydantic import SecretStr

USER_ACCOUNTS_COLLECTION_NAME = APP_CONFIG.database.user_accounts_collection_name
REFRESH_TOKEN_EXPIRE_DAYS = APP_CONFIG.auth.refresh_token_expire_days
PASSWORD_RESET_COLLECTION_NAME = APP_CONFIG.database.password_reset_collection_name
RESET_PASSWORD_LINK_EXPIRE_MINUTES = APP_CONFIG.auth.reset_password_link_expire_minutes

# RATE LIMITS
RATE_LIMIT_CONFIG = APP_CONFIG.redis_config.rate_limits


ENV = APP_CONFIG.env_config.app_environment

FRONTEND_URL = APP_CONFIG.domain.frontend_domain_dev.lower() if ENV in ["dev","development"] else APP_CONFIG.domain.frontend_domain_prod

from src.email_utils.sender import WELCOME_EMAIL_FILE_NAME, send_email

RESET_PASSWORD_EMAIL_FILE_NAME = "reset_password.html"

def create_auth_router(limiter:Limiter)->APIRouter:
    '''
    Factory function for creating auth router with an injected rate limiter.
    Allows different Redis backends to be used per environment (e.g. localhost/memory for tests, prod URI for production).

    :param limiter: Configured SlowAPI Limiter instance to use for rate limiting
    :type limiter: Limiter
    :return: APIRouter with all auth endpoints registered
    :rtype: APIRouter
    '''
    router = APIRouter()
    # limiter = create_rate_limiter(storage_uri=redis_rl_storage_uri)

    router.startup()

    #create user
    @router.post("/add_user")
    @limiter.limit(RATE_LIMIT_CONFIG.sign_up_limit)
    async def add_user(request:Request,user_sign_up_form:UserSignUpForm,background_tasks:BackgroundTasks,database:AsyncDatabase=Depends(create_or_get_database))->JSONResponse:
        '''
            Add new user to the database 

            :param user_sign_up_form: user inputs from the 'sign up' form
            :type user_sign_up_form: UserSignUpForm - Details of form that the user filled in 
            :param user_collection:  Collection in database which stores user info
            :type user_collection: pymongo.asynchronous.collection.AsyncCollection
            
        '''

        main_database = database
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

    @router.post("/login_with_access_token")
    @limiter.limit(RATE_LIMIT_CONFIG.login_limit)
    async def login_with_access_token(request:Request,database:AsyncDatabase=Depends(create_or_get_database),form_data: OAuth2PasswordRequestForm = Depends())->JSONResponse:
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
                
                # boolean checking which environment we are in. If in dev environment, use http. If in prod, use https
                secure = ENV not in ["dev", "development"]
                
                
                # not sending refresh token to the client - setting to http only (stop javascript based attacks).
                # storing refresh token in browser cookie
                

                response.set_cookie(
                    key="refresh_token",value=refresh_token, httponly=True, samesite="lax", max_age=max_age,secure=secure

                )
                print("cookie set on response")

    
                return response
            else:
                return JSONResponse(content={"message":"Incorrect email or password"}, status_code=401)
            
        else:
            return JSONResponse(content={"message":"Incorrect email or password"}, status_code=401)



    @router.post("/refresh")
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
        # check that the user associated with the refresh token exists in the database , and that the refresh token provided matches the (hashed) refresh token stored in database for that user (verify that the refresh token is valid and has not been rotated/invalidated by a new login or refresh)
        user_collection = database[USER_ACCOUNTS_COLLECTION_NAME]
        user_info = await user_collection.find_one({"_id": user["_id"]})
        stored_refresh_token_hashed = user_info.get("refresh_token")

        # token field removed from logout
        if not stored_refresh_token_hashed:
            raise HTTPException(status_code=401, detail="Refresh token has been rotated")

        if not is_correct_token(token_string=refresh_token, stored_hash=stored_refresh_token_hashed):
            # potential token theft — invalidate everything if old refresh token is being used by someone else after a new one has already been issued.
            await user_collection.update_one(
                {"_id": user["_id"]},
                {"$unset": {"refresh_token": ""}}
            )
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = await create_access_token(data={"sub":str(user["_id"])})
        new_refresh_token = await create_refresh_token(data={"sub": str(user["_id"])})

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



    @router.get("/me")
    async def get_user(user = Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database)):
        '''
        Endpoint to verify that we can retrieve the current user from the JWT token
        '''
        if user is None:
            raise HTTPException(status_code=401,detail="Invalid authentication credentials")
        
        return JSONResponse(content={"user_email":user["email"]},status_code=200)



    @router.post("/logout")
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




    @router.post("/send_change_password_link")
    @limiter.limit(RATE_LIMIT_CONFIG.send_password_change_limit)
    async def send_change_password_link(request:Request, user_email:UserEmail, background_tasks:BackgroundTasks, database=Depends(create_or_get_database)):
        '''
            Endpoint to send a link to user's email if they need to change their password. Note that this endpoint does NOT
            reset the password, but it sends a link to a user's email address if they have a registered account,
            and the link will allow them to reset the password
        '''
        email = user_email.email
        users_collection = database[USER_ACCOUNTS_COLLECTION_NAME]
        user_exists = await check_if_email_already_in_use(email_input=email, collection=users_collection)

        if user_exists:
            logging.info("Generating token for password reset")
            token = str(uuid.uuid4())
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_PASSWORD_LINK_EXPIRE_MINUTES)

            # store opaque token in MongoDB — one time use, expires in 20 minutes
            reset_collection = database[PASSWORD_RESET_COLLECTION_NAME]

            # invalidate any existing reset token for this user (if user clicks more than once in short time span)
            await reset_collection.delete_many({"email": email})
            
            await reset_collection.insert_one({"token": token, "email": email, "expires_at": expires_at})

            reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
            logging.info("Sending password reset link")
            background_tasks.add_task(send_email, recipients=[email], subject="Reset your password", context={"reset_link": reset_link}, html_file_name=RESET_PASSWORD_EMAIL_FILE_NAME)

        # always return 200 — deliberately ambiguous so attacker cannot infer if email address is registered
        return JSONResponse(content={"message": f"Thank you. If your email has a registered TWT fitness account, you should receive an email with a link to reset your password. The link will expire after {RESET_PASSWORD_LINK_EXPIRE_MINUTES} minutes."}, status_code=200)
        


    
    @router.post("/reset_password")
    @limiter.limit(RATE_LIMIT_CONFIG.send_password_change_limit)
    async def reset_password(request:Request, reset_password_form:UserResetPasswordForm,database=Depends(create_or_get_database)):

        '''
            Reset user password 

            :param reset_password_form: Form containing user email, and their desired new password (along with password reset token)
            :param database: Database containing collection with reset tokens 
        
        '''
        # token for resetting password 
        token = reset_password_form.token
        new_password = reset_password_form.new_password
        confirm_new_password = reset_password_form.confirm_new_password

        # look up token in reset collection
        reset_collection = database[PASSWORD_RESET_COLLECTION_NAME]
        reset_record = await reset_collection.find_one({"token": token})

        # if token invalid or expired, (e.g. user tries to reset after token expired), give an error 
        if not reset_record or reset_record["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            logging.info("Invalid or expired reset token detected")
            raise HTTPException(status_code=401, detail="The current reset password link has expired or is invalid. If you wish to reset your password, send a new request.")

        user_email = reset_record["email"]
        users_collection = database[USER_ACCOUNTS_COLLECTION_NAME]

        input_format_error_messages = []

        is_password_valid_format = validate_password_format(password=new_password)
        if not is_password_valid_format:
            input_format_error_messages.append("Password is not valid format. It must contain:\n 1. lowercase and uppercase letters\n 2. At least 8 characters\n 3. at least one number\n 4. At least 1 special character")

        passwords_match = check_if_passwords_match(password=new_password, confirm_password=confirm_new_password)
        if not passwords_match:
            input_format_error_messages.append("'Password' and 'Confirm Password' fields do not match")

        if not (passwords_match and is_password_valid_format):
            input_format_error_messages_str = " | ".join(input_format_error_messages)
            error_code = 400 if "do not match" in input_format_error_messages_str.lower() else 422
            return JSONResponse(content={"message": f"Could not reset password: {input_format_error_messages_str}"}, status_code=error_code)

        # hash new password and get user
        new_password_hash = hash_password(password_string=new_password)
        user_info = await users_collection.find_one(filter={"email": user_email}, projection={"_id": True})

        # update password
        await users_collection.update_one(filter={"_id": user_info["_id"]}, update={"$set": {"password": new_password_hash}})

        # invalidate all existing sessions - remove refresh token from user document in MongODB
        await users_collection.update_one(filter={"_id": user_info["_id"]}, update={"$unset": {"refresh_token": ""}})

        # delete reset token — once it has been set (prevents re-use)
        await reset_collection.delete_one({"token": token})

        return JSONResponse(content={"message": "Your password has successfully been reset. Please sign in with your new credentials"}, status_code=200)

    return router
