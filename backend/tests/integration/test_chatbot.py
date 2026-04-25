from src.database.connection import get_mongo_client, create_or_get_database, create_or_get_collection
from src.chatbot.chat_history import get_all_stored_user_chats
from src.chatbot.chat_response import stream_chatbot_response
from src.schemas import  ClientForm
from src.app_setup import create_app

from src.config import APP_CONFIG

MONGO_DB_CONNECTION_STRING = APP_CONFIG.database.mongo_db_connection_string.get_secret_value()
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name
TEST_MONGO_VECTOR_INDEX_NAME = APP_CONFIG.database.test_mongo_vector_index_name
TEST_DATABASE_NAME  = APP_CONFIG.database.test_database_name
TEST_USER_EMAIL = APP_CONFIG.email.test_user_email
TEST_USER_PASSWORD = APP_CONFIG.email.test_user_password.get_secret_value()

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

    async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
        database = mongo_client[TEST_DATABASE_NAME]
        yield database
    
test_app = create_app()
test_app.state.user_based_rate_limiter.enabled = False
test_app.state.ip_rate_limiter.enabled = False

test_app.dependency_overrides[create_or_get_database] = create_or_get_test_database


@pytest.fixture
def login_test_user():

    with TestClient(app=test_app) as client:

        # Login to get a valid access token - using test credentials 
        login_response = client.post(url="/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":TEST_USER_PASSWORD})
        login_response_json = login_response.json()
        login_headers = {"Authorization": f"Bearer {login_response_json['access_token']}"} 
        return login_headers


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
        injuries="None")



@pytest.mark.asyncio
async def test_user_chats_retrieval(login_test_user):
    '''
        Test retrieval of stored user chats from the database
        Assumes there is pre-existing chat data for the test user
    '''

    with TestClient(app=test_app) as client:
        # First, login to get a valid access token
        # login_response = client.post(url="/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":TEST_USER_PASSWORD})
        # login_response_json = login_response.json()
          
        # Use the access token to get current user info
 
        response_1 = client.post(url=f"/get_stored_user_chats",headers=login_test_user)
        stored_chats = response_1.json()

        assert response_1.status_code == 200
        assert  len(stored_chats) > 0 #assuming there are multiple stored chats for the test user in the database
        #check that the response container expected fields - conversation_id, email, messages (list of messages in the conversation), timestamp
        assert "conversation_id" in stored_chats[0].keys()  
        assert "email" in stored_chats[0].keys() 
        assert "messages" in stored_chats[0].keys() 

@pytest.mark.asyncio
async def test_get_specific_stored_chat(login_test_user):
    '''
        Test retrieval of a specific stored user chat from the database
        Assumes there is pre-existing chat data for the test user
    '''

    with TestClient(app=test_app) as client:

        # Use the access token to get current user info

    
        response = client.post(url=f"/get_chat_history",headers=login_test_user,json={"conversation_id":TEST_CONVERSATION_ID})
        assert response.status_code == 200
        assert  "hi" in response.json()[0]["message"].lower() # assuming first message is a greeting from the chatbot saying ""Hi, I'm Monyai your fitness assistant!"



@pytest.mark.asyncio
async def test_create_new_chat(login_test_user):
    '''
        test successful creation of new chat
    '''
    with TestClient(app=test_app) as client:


        create_new_chat_response = client.post(url=f"/create_new_chat",headers=login_test_user)
        create_new_chat_response_json = create_new_chat_response.json()

        assert create_new_chat_response.status_code == 201
        assert "conversation_id" in create_new_chat_response_json






@pytest.mark.asyncio
@pytest.mark.llm_call
async def test_stream_chatbot_response(test_client_form,login_test_user):
    '''
        Test that chatbot gives appropriate response
    
    '''

    with TestClient(app=test_app) as client:

        user_query = "Should I cut carbs to lose fat?"

        user_message = {'message':user_query,'timestamp':str(datetime.now()),'type':'user'}

        #example chats - mimicks the structure of chats extracted from the database
        test_chat_history = [
        {"type":"bot","message":"Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.",'timestamp': '2026-01-01 11:37:11.409816'}]

        dummy_conversation_id  = str(uuid.uuid4())


        # send a sample
        with client.stream("POST","/chat",json={
            "user_message": user_message,
            "chat_history": test_chat_history,
            "client_form": test_client_form.model_dump(),
            "conversation_id": dummy_conversation_id
            },
            headers=login_test_user) as response:

            chunks = list(response.iter_text())

            

            print(chunks)
            assert all(isinstance(chunk,str) for chunk in chunks)
            assert "__REFS__" in chunks[0]


@pytest.mark.asyncio
async def test_attempt_chatbot_not_authenticated(test_client_form):
    '''

    Test the 401 error raised when user tries to use chatbot without first being signed in
    
    
    '''
    with TestClient(app=test_app) as client:

        user_query = "Should I cut carbs to lose fat?"

        user_message = {'message':user_query,'timestamp':str(datetime.now()),'type':'user'}

        #example chats - mimicks the structure of chats extracted from the database
        test_chat_history = [
        {"type":"bot","message":"Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.",'timestamp': '2026-01-01 11:37:11.409816'}]

        dummy_conversation_id  = str(uuid.uuid4())


        response = client.post("/chat",json={
            "user_message": user_message,
            "chat_history": test_chat_history,
            "client_form": test_client_form.model_dump(),
            "conversation_id": dummy_conversation_id
            })

        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

