#test the database connection

from src.database.connection import get_mongo_client

import pytest_asyncio
import pytest
from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
import logging


#testing the connection has been successful - signal to pytest that it's an async function 
@pytest.mark.asyncio
async def test_successful_database_connetion(get_mongo_client):
    #attempt to connect to database
    # mongo_client =  connect_to_database()
    assert isinstance(get_mongo_client[0],AsyncMongoClient)
    assert get_mongo_client[1]["ok"] == 1.0
    
    

