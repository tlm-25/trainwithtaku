from src.retrieval import mongo_db_vector_search
from src.config import MONGO_DB_CONNECTION_STRING,TEST_DATABASE_NAME, TEST_CHAT_COLLECTION_NAME,TEST_VECTOR_STORE_COLLECTION_NAME,TEST_MONGO_VECTOR_INDEX_NAME, TOP_K
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
import pytest
async def create_or_get_test_database():
    '''
    Database for testing only
    '''
    try:
        async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
            database = mongo_client[TEST_DATABASE_NAME]
            yield database
    
    except Exception as e:
          raise RuntimeError(f"failed to connect to database {TEST_DATABASE_NAME}: {e}")


@pytest.mark.asyncio
async def test_vector_search():
    '''
        Test the vector search retrieval
    
    '''
    test_query = "should I do cardio on a bulk?"
    #get the test database
    test_mongo_database = await create_or_get_test_database().__anext__()
    test_vector_store_collection = test_mongo_database[TEST_VECTOR_STORE_COLLECTION_NAME]

    retrieved_documents = await mongo_db_vector_search(query=test_query,vector_store_collection=test_vector_store_collection,mongo_index_name=TEST_MONGO_VECTOR_INDEX_NAME)

    assert len(retrieved_documents) == TOP_K



