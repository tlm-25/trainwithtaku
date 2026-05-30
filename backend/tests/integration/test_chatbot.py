from src.database.connection import get_mongo_client, create_or_get_database, create_or_get_collection
from src.chatbot.chat_history import get_all_stored_user_chats
from src.chatbot.chat_response import stream_chatbot_response
from src.schemas import  ClientForm
from src.app_setup import create_app

from src.config import APP_CONFIG

import pytest_asyncio
MONGO_DB_CONNECTION_STRING = APP_CONFIG.database.mongo_db_connection_string.get_secret_value()
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name
TEST_MONGO_VECTOR_INDEX_NAME = APP_CONFIG.database.test_mongo_vector_index_name
TEST_DATABASE_NAME  = APP_CONFIG.database.test_database_name
TEST_USER_EMAIL = APP_CONFIG.email.test_user_email
TEST_USER_PASSWORD = APP_CONFIG.email.test_user_password.get_secret_value()
CHAT_COLLECTION_NAME = APP_CONFIG.database.chat_collection_name
TEST_CONVERSATION_ID = APP_CONFIG.chatbot.test_conversation_id

from fastapi.testclient import TestClient

from pymongo import AsyncMongoClient
from datetime import datetime
import pytest
import uuid


async def create_or_get_test_database():
    '''
    Database for testing only
    '''
    async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING, serverSelectionTimeoutMS=10000) as mongo_client:
        database = mongo_client[TEST_DATABASE_NAME]
        yield database


# Single module-level app instance with all overrides applied once
test_app = create_app()
test_app.dependency_overrides[create_or_get_database] = create_or_get_test_database
test_app.state.user_based_rate_limiter.enabled = False
test_app.state.ip_rate_limiter.enabled = False




@pytest.fixture
def test_client():
    # Wraps the module-level test_app â€” never creates a new instance
    return TestClient(app=test_app)


@pytest.fixture
def login_test_user(test_client):
    login_response = test_client.post(
        url="/api/login_with_access_token",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    assert login_response.status_code == 200, (
        f"Test user login failed with {login_response.status_code}: {login_response.json()}"
    )
    login_response_json = login_response.json()
    return {"Authorization": f"Bearer {login_response_json['access_token']}"}


@pytest.fixture
def test_client_form():
    return ClientForm(
        email="test@gmail.com",
        age=23,
        gender="male",
        allergies="None",
        current_bodyweight_kg=70,
        height_cm=175,
        current_activity_level="sedentary",
        current_occupation="office worker",
        current_average_steps_per_day=3000,
        primary_fitness_goal="fat loss",
        days_available_to_train_per_week=3,
        preferred_foods="chicken, rice, vegetables",
        preferred_no_meals=3,
        preferred_location="home",
        equipment_available="dumbbells, resistance bands",
        dietary_restrictions="None",
        injuries="None"
    )


@pytest_asyncio.fixture
async def owned_conversation_id():
    """
    Pre-create a conversation document in the test DB owned by the test user,
    so the ownership check in /chat passes.
    """
    async with AsyncMongoClient(
        host=MONGO_DB_CONNECTION_STRING, serverSelectionTimeoutMS=10000
    ) as mongo_client:
        db = mongo_client[TEST_DATABASE_NAME]
        conversation_id = str(uuid.uuid4())
        await db[CHAT_COLLECTION_NAME].insert_one({
            "conversation_id": conversation_id,
            "email": TEST_USER_EMAIL,
            "messages": []
        })

        yield conversation_id

        # cleanup
        await db[CHAT_COLLECTION_NAME].delete_one({"conversation_id": conversation_id})




@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_user_chats_retrieval(test_client, login_test_user):
    '''
        Test retrieval of stored user chats from the database
        Assumes there is pre-existing chat data for the test user
    '''
    response_1 = test_client.post(url="/api/get_stored_user_chats", headers=login_test_user)
    stored_chats = response_1.json()

    assert response_1.status_code == 200
    # assuming there are multiple stored chats for the test user in the database
    assert len(stored_chats) > 0  
    # check that the response contains expected fields - conversation_id, email, messages (list of messages in the conversation), timestamp
    assert "conversation_id" in stored_chats[0].keys()
    assert "email" in stored_chats[0].keys()
    assert "messages" in stored_chats[0].keys()



@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_get_specific_stored_chat(test_client, login_test_user):
    '''
        Test retrieval of a specific stored user chat from the database
        Assumes there is pre-existing chat data for the test user
    '''
    response = test_client.post(
        url="/api/get_chat_history",
        headers=login_test_user,
        json={"conversation_id": TEST_CONVERSATION_ID}
    )
    assert response.status_code == 200
    # assuming first message is a greeting from the chatbot saying "Hi, I'm Monyai your fitness assistant!"
    assert "hi" in response.json()[0]["message"].lower()  



@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_create_new_chat(test_client, login_test_user):
    '''
        test successful creation of new chat
    '''
    create_new_chat_response = test_client.post(url="/api/create_new_chat", headers=login_test_user)
    create_new_chat_response_json = create_new_chat_response.json()

    assert create_new_chat_response.status_code == 201
    assert "conversation_id" in create_new_chat_response_json


@pytest.mark.mongodb
@pytest.mark.asyncio
@pytest.mark.llm_call
async def test_stream_chatbot_response(test_client, test_client_form, login_test_user, owned_conversation_id):
    '''
        Test that chatbot gives appropriate response
    
    '''
    user_query = "Should I cut carbs to lose fat?"

    user_message = {'message': user_query, 'timestamp': str(datetime.now()), 'type': 'user'}

    # example chats - mimicks the structure of chats extracted from the database
    test_chat_history = [
        {"type": "bot", "message": "Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.", 'timestamp': '2026-01-01 11:37:11.409816'}
    ]

    with test_client.stream("POST", "/api/chat", json={
        "user_message": user_message,
        "chat_history": test_chat_history,
        "client_form": test_client_form.model_dump(),
        "conversation_id": owned_conversation_id
    }, headers=login_test_user) as response:
        assert response.status_code == 200
        chunks = list(response.iter_text())
        print(chunks)
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert "__REFS__" in chunks[0]



@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_attempt_chatbot_not_authenticated(test_client, test_client_form):
    '''

    Test the 401 error raised when user tries to use chatbot without first being signed in
    
    
    '''
    user_query = "Should I cut carbs to lose fat?"

    user_message = {'message': user_query, 'timestamp': str(datetime.now()), 'type': 'user'}

    # example chats - mimicks the structure of chats extracted from the database
    test_chat_history = [
        {"type": "bot", "message": "Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.", 'timestamp': '2026-01-01 11:37:11.409816'}
    ]

    dummy_conversation_id = str(uuid.uuid4())

    response = test_client.post("/api/chat", json={
        "user_message": user_message,
        "chat_history": test_chat_history,
        "client_form": test_client_form.model_dump(),
        "conversation_id": dummy_conversation_id
    })

    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()



@pytest.mark.mongodb
@pytest.mark.asyncio
async def test_chat_ownership_check(test_client, login_test_user, test_client_form):
    """
    Sending a message to a conversation owned by a different user should return 403.
    """
    async with AsyncMongoClient(
        host=MONGO_DB_CONNECTION_STRING, serverSelectionTimeoutMS=10000
    ) as mongo_client:
        db = mongo_client[TEST_DATABASE_NAME]
        conversation_id = str(uuid.uuid4())
        await db[CHAT_COLLECTION_NAME].insert_one({
            "conversation_id": conversation_id,
            "email": "someone_else@example.com",  # different owner
            "messages": []
        })

    user_message = {'message': "test", 'timestamp': str(datetime.now()), 'type': 'user'}

    with test_client.stream("POST", "/api/chat", json={
        "user_message": user_message,
        "chat_history": [],
        "client_form": test_client_form.model_dump(),
        "conversation_id": conversation_id
    }, headers=login_test_user) as response:
        assert response.status_code == 403

    # cleanup
    async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING) as mongo_client:
        await mongo_client[TEST_DATABASE_NAME][CHAT_COLLECTION_NAME].delete_one(
            {"conversation_id": conversation_id}
        )


