from pymongo import AsyncMongoClient, MongoClient
import os 
from src.config import MONGO_DB_CONNECTION_STRING
import pytest_asyncio
import logging
#mark with pytest_asyncio so that the result can be passed into pytest function for testing - dependency injection - makes the client accessible in async tests
@pytest_asyncio.fixture
async def get_mongo_client():
    '''
        Open connection to mongoDB database
    '''
    try:
        # using 'async with' and 'yield' so that the client is available to use in a another function, and depedency injection used to access the connection while it's open:  
        # Makes connection useable in fastAPI endpoints 
        logging.info("connecting to databse")
        async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
            
            result = await mongo_client.admin.command('ping')
            print(result)
            print(type(mongo_client))
            logging.info("succesfully connected to database")
            yield mongo_client,result
            
        
    except Exception as e:
        yield f"failed to connect {e}"


