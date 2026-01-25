#Tests for uploading to vector store
from src.main import app
from src.database.connection import create_or_get_database
from src.config import VECTOR_STORE_COLLECTION_NAME, TEST_DATABASE_NAME, MONGO_DB_CONNECTION_STRING
from src.database.vector_store import upload_to_vector_store, generate_documents
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
async def test_succesful_document_upload_web():
    
    test_mongo_database = await create_or_get_test_database().__anext__()
    test_url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4090010/"
    test_vector_store_collection = test_mongo_database[VECTOR_STORE_COLLECTION_NAME]
    original_collection_length = await test_vector_store_collection.count_documents({})
    documents = await generate_documents(source_type="web",url=test_url)
    response = await upload_to_vector_store(database=test_mongo_database,documents=documents,collection_name=VECTOR_STORE_COLLECTION_NAME)
    new_collection_length = await test_vector_store_collection.count_documents({})
    #ensure success message is sent
    assert "success" in response.lower()
    #ensure that new documents were added to the collection 
    assert new_collection_length > original_collection_length

@pytest.mark.asyncio
async def test_succesful_document_upload_pdf():
    
    test_mongo_database = await create_or_get_test_database().__anext__()
    file_path = "pdf_documents/twt_hench_head_start.pdf"
    test_vector_store_collection = test_mongo_database[VECTOR_STORE_COLLECTION_NAME]
    original_collection_length = await test_vector_store_collection.count_documents({})
    documents = await generate_documents(source_type="pdf",pdf_path=file_path)
    response = await upload_to_vector_store(database=test_mongo_database,documents=documents,collection_name=VECTOR_STORE_COLLECTION_NAME)
    new_collection_length = await test_vector_store_collection.count_documents({})
    #ensure success message is sent
    assert "success" in response.lower()
    #ensure that new documents were added to the collection 
    assert new_collection_length > original_collection_length
