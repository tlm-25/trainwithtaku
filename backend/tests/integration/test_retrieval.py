from src.search.retrieval import  CustomAsyncMongoDBAtlasRetriever

from src.config import APP_CONFIG

MONGO_DB_CONNECTION_STRING = APP_CONFIG.database.mongo_db_connection_string.get_secret_value()
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name
TEST_MONGO_VECTOR_INDEX_NAME = APP_CONFIG.database.test_mongo_vector_index_name
TEST_DATABASE_NAME  = APP_CONFIG.database.test_database_name
TEST_USER_EMAIL = APP_CONFIG.email.test_user_email
TEST_USER_PASSWORD = APP_CONFIG.email.test_user_password.get_secret_value()
TOP_K = APP_CONFIG.chatbot.top_k



from src.schemas import ClientForm
from langchain.schema import Document
from pymongo import AsyncMongoClient
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
@pytest.mark.mongodb
async def test_vector_search():
    '''
        Test the vector search retrieval
    
    '''
    test_query = "should I do cardio on a bulk?"
    #get the test database
    test_mongo_database = await create_or_get_test_database().__anext__()
    #get the test collection
    test_vector_store_collection = test_mongo_database[VECTOR_STORE_COLLECTION_NAME]



    # async mongo driver 
    async_mongodb_retriever = CustomAsyncMongoDBAtlasRetriever(vector_store_collection=test_vector_store_collection,mongo_index_name=TEST_MONGO_VECTOR_INDEX_NAME)



    retrieved_documents = await async_mongodb_retriever.ainvoke(input=test_query)


    
    
    assert len(retrieved_documents) == TOP_K
    assert isinstance(retrieved_documents[0],Document)
    assert isinstance(retrieved_documents[0].page_content,str)



@pytest.mark.asyncio
async def test_failed_attempted_synchronous_vector_search():
    '''
        Test the correct error is raised if user attempts to use public get_relevant_documents method 
    
    '''
    test_query = "should I do cardio on a bulk?"
    #get the test database
    test_mongo_database = await create_or_get_test_database().__anext__()
    #get the test collection
    test_vector_store_collection = test_mongo_database[VECTOR_STORE_COLLECTION_NAME]

    # async mongo driver 
    async_mongodb_retriever = CustomAsyncMongoDBAtlasRetriever(vector_store_collection=test_vector_store_collection,mongo_index_name=TEST_MONGO_VECTOR_INDEX_NAME)


    
    with pytest.raises(NotImplementedError,match="This class is async only - please user ainvoke instead"):
        retrieved_documents =  async_mongodb_retriever.invoke(query=test_query)




