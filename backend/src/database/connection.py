from pymongo import AsyncMongoClient, MongoClient
import os 
from src.config import APP_CONFIG
MONGO_DB_CONNECTION_STRING = APP_CONFIG.database.mongo_db_connection_string.get_secret_value()
DATABASE_NAME = APP_CONFIG.database.database_name
TEST_DATABASE_NAME = APP_CONFIG.database.test_database_name
import pytest_asyncio
import logging


#function for connection to client, database and containers - creating seperate functions for ease of debugging and testing for CI/CD 

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
        raise(f"failed to connect {e}")



async def create_or_get_database():
    '''
        Create new database or get exsiting database within the collection
    
    '''
    async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
        database = mongo_client[DATABASE_NAME]
        yield database






async def create_or_get_collection(collection_name:str):
    '''
        Create new collection or get exsiting collection
        collection_name (str) - name of function that we want to get or collect
    '''   
     
    try: 
        async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
            database = mongo_client[DATABASE_NAME]

            collection = database[collection_name]
            yield collection
    except Exception as e:
         raise RuntimeError(
            f"Failed to access collection '{collection_name}' in database '{DATABASE_NAME}': {e}"
        )
         

    
               
        
    