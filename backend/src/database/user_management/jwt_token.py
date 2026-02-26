
from src.config import JWT_SECRET_KEY,ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, USER_ACCOUNTS_COLLECTION_NAME
from src.schemas import TokenData, UserInDB,User
from src.database.user_management.utils import check_if_email_already_in_use
from src.database.connection import create_or_get_database
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from datetime import datetime, timedelta, timezone
# from jose import JWTError
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from jwt.exceptions import InvalidTokenError
from bson import ObjectId
from bson.errors import InvalidId
oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data:dict):
    '''

        Creating json web access token for user who logs in - access for 
        certain amount of time before having to log in again
    
    
    '''
    
    #create a shallow copy of dictionary data - avoid mutating the original data
    data_to_encode = data.copy()


    #set expiry time of token for certain user
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({"exp":expire})

    #generate json web token for access for a specific user
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
                                  
