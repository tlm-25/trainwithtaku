from src.database.connection import get_mongo_client, create_or_get_database, create_or_get_collection
from src.chatbot.chat_history import get_all_stored_user_chats
from src.config import CHAT_COLLECTION_NAME, TEST_CHAT_COLLECTION_NAME, TEST_DATABASE_NAME, MONGO_DB_CONNECTION_STRING
from src.schemas import UserEmail, Conversation
from src.main import app



from fastapi.testclient import TestClient

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

import pytest
import uuid

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

app.dependency_overrides[create_or_get_database] = create_or_get_test_database

#TODO
@pytest.mark.asyncio
async def test_user_chats_retrieval():
    '''
        Test retrieval of stored user chats from the database
        Assumes there is pre-existing chat data for the test user
    '''

    with TestClient(app=app) as client:
        test_user_1 = UserEmail(email="test1@gmail.com")
        test_user_mock_json_1 = test_user_1.model_dump()       
        response_1 = client.post(url=f"/get_stored_user_chats",json=test_user_mock_json_1)

        test_user_2 = UserEmail(email="test2@gmail.com")
        test_user_mock_json_2 = test_user_2.model_dump()       
        response_2 = client.post(url=f"/get_stored_user_chats",json=test_user_mock_json_2)


        assert response_1.status_code == 200
        assert  len(response_1.json()) == 2 #assuming there are 2 stored chats for the test user in the database
        assert response_1.status_code == 200
        assert  len(response_2.json()) == 1 #assuming there is 1 stored chat for the test user in the database

@pytest.mark.asyncio
async def test_get_specific_stored_chat():
    '''
        Test retrieval of a specific stored user chat from the database
        Assumes there is pre-existing chat data for the test user
    '''

    with TestClient(app=app) as client:
        conversation_id = "3434343-34234243-1231"      
        response = client.post(url=f"/get_chat_history/{conversation_id}")
        assert response.status_code == 200
        assert  len(response.json()) == 2 #assuming there are 2 messages in the stored chat for the test conversation id