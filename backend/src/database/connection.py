from pymongo import AsyncMongoClient, MongoClient
import os 
from src.config import MONGO_DB_CONNECTION_STRING, DATABASE_NAME
import pytest_asyncio
import logging


#mark with pytest_asyncio so that the result can be passed into pytest function for testing - dependency injection - makes the client accessible in async tests
@pytest_asyncio.fixture
async def get_mongo_client():
    
    '''
        Open connection to mongoDB cluster
    '''
    #check if Mongo connection string is not set
    if not MONGO_DB_CONNECTION_STRING or MONGO_DB_CONNECTION_STRING is None:
                raise RuntimeError("Missing MongoDB connection string")
    try:
        
        # using 'async with' and 'yield' so that the client is available to use in a another function, and depedency injection used to access the connection while it's open:  
        # Makes connection useable in fastAPI endpoints 
        logging.info("connecting to MongoDB cluster")
        async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
            
            
            result = await mongo_client.admin.command('ping')
            print(result)
            print(type(mongo_client))
            logging.info("succesfully connected to cluster")
            print("succesfully connected to cluster")
            yield mongo_client,result
            
        
    except Exception as e:
        logging.error(f"failed to connect: {e}")
        yield f"failed to connect {e}"

@pytest_asyncio.fixture
async def create_or_get_database():
    '''
        Create new database or get exsiting database
    
    '''
    try:
        async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
            database = mongo_client[DATABASE_NAME]
            yield database
    
    except Exception as e:
          yield f"failed to connect to database {DATABASE_NAME}: {e}"

# @pytest_asyncio.fixture
# async def create_or_get_container():
#      '''
#         Create new database or get exsiting database
#     '''   
     
#      try: 
        
    