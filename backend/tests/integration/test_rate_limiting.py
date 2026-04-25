import pytest
from fastapi.testclient import TestClient
from src.database.connection import get_mongo_client, create_or_get_database, create_or_get_collection

from src.config import APP_CONFIG
from datetime import datetime
import redis
import uuid
from pymongo import AsyncMongoClient
# from src.rate_limiter import limiter

from src.app_setup import create_app
import logging

TEST_USER_EMAIL = APP_CONFIG.email.test_user_email
TEST_USER_PASSWORD = APP_CONFIG.email.test_user_password.get_secret_value()
MONGO_DB_CONNECTION_STRING = APP_CONFIG.database.mongo_db_connection_string.get_secret_value()
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name
TEST_DATABASE_NAME  = APP_CONFIG.database.test_database_name
REDIS_CONNECTION_STRING = APP_CONFIG.redis_config.redis_connection_string.get_secret_value()

TEST_REDIS_CONNECTION_STRING = None


async def create_or_get_test_database():
    '''
    Database for testing only
    '''

    async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
        database = mongo_client[TEST_DATABASE_NAME]
        yield database


@pytest.fixture
def test_client():
    test_app = create_app()
    test_app.dependency_overrides[create_or_get_database] = create_or_get_test_database

    return TestClient(app=test_app)


@pytest.fixture
def login_test_user(test_client):
    login_response = test_client.post(
        "/login_with_access_token",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    print(login_response.json())
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


@pytest.mark.asyncio
@pytest.mark.slow
async def test_simulate_brute_force_attack(test_client):
    '''
        Simulate brute force attack where an attacker is trying to guess a password
        Return 401 error for the first 10
        When the 11th attempt is made within a minute, a 429 error should be returned 
        
        If on windows, ensure that focker desktop is open and you are logged in. Docker will be needed 
        to spim u hte local redis server for this test 
        
        Ensure thethe local redis instance is running 
        to turn on local redis server run "docker run -d -p 6379:6379 --name some-redis redis" 
    
    '''


    # first 10 login attemps (incorrect password)
    for i in range(0,10):

        print (f"attempt {i}")
        

        password_guess = str(uuid.uuid4())
        response = test_client.post("/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":password_guess})
    
        assert response.status_code == 401

    #ensure a 429 error code is returned with rate limit in reached and expected error message
    response = test_client.post("/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":password_guess})
    message = response.json()["message"].lower()
    logging.info(f"message: {message}")
    assert response.status_code== 429
    assert "too many login attempts." in message


@pytest.mark.asyncio    
@pytest.mark.llm_call
@pytest.mark.slow
async def test_user_chatbot_rate_limit(test_client,login_test_user):
    '''
    Confirm that user based chat limiting enforced 
    
    '''

    for i in range(0,3):
        user_query = "Should I cut carbs to lose fat?"

        user_message = {'message':user_query,'timestamp':str(datetime.now()),'type':'user'}

        #example chats - mimicks the structure of chats extracted from the database
        test_chat_history = [
        {"type":"bot","message":"Hi",'timestamp': '2026-01-01 11:37:11.409816'}]

        dummy_conversation_id  = str(uuid.uuid4())
       # send a sample
        with test_client.stream("POST","/chat",json={
            "user_message": user_message,
            "chat_history": test_chat_history,
            "conversation_id": dummy_conversation_id
            },
            headers=login_test_user) as response:

            #check that response given
            chunks = list(response.iter_text())
            assert all(isinstance(chunk,str) for chunk in chunks)

    response =  test_client.post("/chat",json={
            "user_message": user_message,
            "chat_history": test_chat_history,
            "conversation_id": dummy_conversation_id
            }, headers=login_test_user) 
    

    # Ensure that rate limit is enforced for user

    message = response.json()["message"].lower()
    logging.info(f"message: {message}")
    assert response.status_code== 429
    assert "message allowance reached" in message







