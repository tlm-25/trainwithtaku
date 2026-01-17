from src.retrieval import  CustomAsyncMongoDBAtlasRetriever
from src.config import MONGO_DB_CONNECTION_STRING,TEST_DATABASE_NAME,TEST_VECTOR_STORE_COLLECTION_NAME,TEST_MONGO_VECTOR_INDEX_NAME, TOP_K
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
async def test_vector_search():
    '''
        Test the vector search retrieval
    
    '''
    test_query = "should I do cardio on a bulk?"
    #get the test database
    test_mongo_database = await create_or_get_test_database().__anext__()
    #get the test collection
    test_vector_store_collection = test_mongo_database[TEST_VECTOR_STORE_COLLECTION_NAME]



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
    test_vector_store_collection = test_mongo_database[TEST_VECTOR_STORE_COLLECTION_NAME]

    # async mongo driver 
    async_mongodb_retriever = CustomAsyncMongoDBAtlasRetriever(vector_store_collection=test_vector_store_collection,mongo_index_name=TEST_MONGO_VECTOR_INDEX_NAME)


    
    with pytest.raises(NotImplementedError,match="This class is async only - please user ainvoke instead"):
        retrieved_documents =  async_mongodb_retriever.invoke(query=test_query)




