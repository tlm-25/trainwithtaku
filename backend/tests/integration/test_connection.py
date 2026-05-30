#test the database connection

from src.database.connection import get_mongo_client, create_or_get_database, create_or_get_collection

import pytest_asyncio
import pytest
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import ConnectionFailure
import logging


#testing the connection ti  has been successful
@pytest.mark.mongodb
@pytest.mark.asyncio # signal to pytest that it's an async function 
async def test_successful_mongo_client_connection(get_mongo_client):
    
    #attempt to connect to MongoDB cluster
    assert isinstance(get_mongo_client[0],AsyncMongoClient)
    assert get_mongo_client[1]["ok"] == 1.0





# # #testing that the database exists and that we can connect to it
# # @pytest.mark.mongodb
# @pytest.mark.asyncio
# # async def test_sucessful_database_connection(create_or_get_database):
# #     assert isinstance(create_or_get_database,AsyncDatabase)



# # @pytest.mark.mongodb
# @pytest.mark.asyncio
# # async def test_sucessful_collection_connection():
# #     #generator object for the get_collection function 
# #     collection_function_gen = create_or_get_collection(collection_name="twt_test")
# #     #get the yielded value from the generator
# #     collection = await collection_function_gen.__anext__()
# #     assert isinstance(collection,AsyncCollection)
