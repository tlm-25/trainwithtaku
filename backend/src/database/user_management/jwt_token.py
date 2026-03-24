
from src.config import (JWT_SECRET_KEY,
                        ACCESS_TOKEN_EXPIRE_MINUTES, 
                        JWT_ALGORITHM, 
                        USER_ACCOUNTS_COLLECTION_NAME, 
                        REFRESH_TOKEN_EXPIRE_DAYS,
                        TOKEN_BLACKLIST_COLLECTION_NAME)


from src.schemas import TokenData, UserInDB,User
from src.database.user_management.utils import check_if_email_already_in_use
from src.database.connection import create_or_get_database
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from datetime import datetime, timedelta, timezone
# from jose import JWTError
import jwt
import uuid
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from jwt.exceptions import InvalidTokenError
from bson import ObjectId
from bson.errors import InvalidId
oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def create_access_token(data:dict)->str:
    '''

        Creating json web access token for user who logs in - access for 
        certain amount of time before having to log in again. 
        This one is short lived
    
    
    '''
    
    #create a shallow copy of dictionary data - avoid mutating the original data
    data_to_encode = data.copy()


    #set expiry time of token for certain user
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({"exp":expire})

    #generate json web token for access for a specific user
    encoded_jwt = jwt.encode(payload=data_to_encode,key=JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)

    return encoded_jwt



async def create_refresh_token(data:dict):
    '''
        Create a refresh token for the user in order to get a new access token
        (access token generally short lived). This way, if a hacker finds out the
        acccess token, they would only have short-lived access to the resource.

        THe refresh token is generated to request a new access token after first one expires
    
    '''
    #create a shallow copy of dictionary data - avoid mutating the original data
    data_to_encode = data.copy()
    #set expiry time of token for certain user
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    data_to_encode.update({"exp":expire, "token_type":"refresh","jti":str(uuid.uuid4())})
    encoded_jwt = jwt.encode(payload=data_to_encode,key=JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)
    return encoded_jwt

    
    # user = get_user(mongo_db,email)

    
    


async def get_user_by_email(email:str,database:AsyncDatabase,user_collection_name:str)->UserInDB:
    '''
    Get user information from email
    
    :param email: Description
    :type email: str
    :param database: Description
    :type database: AsyncDatabase
    :param user_collection_name: Description
    :type user_collection_name: str
    '''
    users_collection = database[user_collection_name]
    check_if_user_exists = await check_if_email_already_in_use(email_input=email,collection=users_collection)
    
    if check_if_user_exists:
        #retriever user info and log them in
        user_info = await users_collection.find_one(filter={"email":email},projection={"_id":False,"user":True,"password":True})
        return UserInDB(**user_info)
    else:
        return None


async def get_current_user(token:str=Depends(oath2_scheme),database:AsyncDatabase=Depends(create_or_get_database)):

    '''
        Get the JWT and retrieve the user. If token is invalid or user does not exist, raise credentials error
    
    '''

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,key=JWT_SECRET_KEY,algorithms=[JWT_ALGORITHM])
        #get user id from payload of the token 
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # structured repressentation of the decoded jwt payload
        token_data = TokenData(user_id=user_id)


    except InvalidTokenError:
        raise credentials_exception
    

    # get user with the user id from the token data - if user doesn't exist, raise credentials exception
    user = await database[USER_ACCOUNTS_COLLECTION_NAME].find_one(
        {"_id": ObjectId(user_id)}
    )
    if user is None:
        raise credentials_exception
    return user
    

async def get_current_active_user(current_user:User = Depends(get_current_user)):
    '''
    Check if the current user is active and not disabled
    
    :param current_user: Description
    :type current_user: User
    '''

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user



async def blacklist_token(jti: str, expiry: datetime, database: AsyncDatabase) -> None:
    """
    Write a JTI to the blacklist collection.
 
    The document carries an "expires_at" field matching the token's own expiry.
    The TTL index on that field (created at startup) automatically deletes the
    document once the token would have expired anyway, so the blacklist never
    grows unboundedly.
 
    :param jti: The unique JWT ID to invalidate.
    :type jti: str
    :param expiry: The token's original expiry datetime (UTC-aware).
    :type expiry: datetime
    :param database: Async MongoDB database instance.
    :type database: AsyncDatabase
    """
    blacklist_collection = database[TOKEN_BLACKLIST_COLLECTION_NAME]
    await blacklist_collection.insert_one({
        "jti": jti,
        "expires_at": expiry,   # TTL index targets this field
    })


async def is_token_blacklisted(jti: str, database: AsyncDatabase) -> bool:
    """
    Return True if the JTI has been blacklisted (i.e. the user has logged out).
 
    :param jti: JWT ID to check.
    :type jti: str
    :param database: Async MongoDB database instance.
    :type database: AsyncDatabase
    :return: True if blacklisted, False otherwise.
    :rtype: bool
    """
    blacklist_collection = database[TOKEN_BLACKLIST_COLLECTION_NAME]
    doc = await blacklist_collection.find_one({"jti": jti})
    return doc is not None



async def verify_token(token:str, expected_token_type:str,database:AsyncDatabase)->dict:
    '''
    Decode and validate a JWT, check the blacklist, then return the user document.

    Raises HTTP 401 if the token is missing, expired, structurally invalid

    :param token: The JWT token to be verified
    :type token:str

    :param expected_token_type: The expected type of token (access/refresh)
    :type expected_token_type:str

    :param database: Async MongoDB database instance.
    :type database: AsyncDatabase

    :return: The raw MongoDB user document
    :rtype: dict

    :raises HTTPException: 401 if validation fails for any reason.
    
    '''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    
    

    try:
       payload = jwt.decode(token,key=JWT_SECRET_KEY,algorithms=[JWT_ALGORITHM])
       
    except InvalidTokenError:
       raise credentials_exception
    

    #get user id from payload of the token
    user_id = payload.get("sub")

    if user_id is None:
        raise credentials_exception
    
    # Check token type

    if payload.get("token_type")!=expected_token_type:
        raise credentials_exception
    
    # chefck blacklist - only refresh for tokens that carry a JTI currently
    jti = payload.get("jti")

    if jti and await is_token_blacklisted(jti=jti, database=database): 
        raise credentials_exception
    
    try:
        object_id = ObjectId(user_id)
    
    except(InvalidId,Exception):
        raise credentials_exception
    
    user = await database[USER_ACCOUNTS_COLLECTION_NAME].find_one({"_id": object_id})

    if user is None:
        raise credentials_exception
    
    # Attach decoded payload so callers (e.g. /logout) can read jti/exp
    # without decoding a second time.
    user["_jwt_payload"] = payload
    return user







    
       


