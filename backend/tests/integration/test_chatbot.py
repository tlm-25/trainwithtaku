from src.database.connection import get_mongo_client, create_or_get_database, create_or_get_collection
from src.chatbot.chat_history import get_all_stored_user_chats
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.chatbot.chat_response import stream_chatbot_response
from src.config import CHAT_COLLECTION_NAME, TEST_CHAT_COLLECTION_NAME, TEST_DATABASE_NAME, MONGO_DB_CONNECTION_STRING
from src.schemas import UserEmail, ClientForm,Conversation
from src.main import app



from fastapi.testclient import TestClient

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
import pytest
import uuid

async def create_or_get_test_database():
    '''
    Database for testing only
    '''

    async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
        database = mongo_client[TEST_DATABASE_NAME]
        yield database
    


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

        assert response_1.status_code == 200
        assert  len(response_1.json()) > 0 #assuming there are multiple stored chats for the test user in the database


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



@pytest.mark.asyncio
async def test_create_new_chat():
    '''
        test successful creation of new chat
    '''
    with TestClient(app=app) as client:
        test_email = "existing_email@gmail.com"
        password = "Codeword1!!"
        # First, login to get a valid access token
        login_response = client.post(url="/login_with_access_token",data={"username":test_email,"password":password})
        login_response_json = login_response.json()

        # Use the access token to get current user info
        headers = {"Authorization": f"Bearer {login_response_json['access_token']}"}


        create_new_chat_response = client.post(url=f"/create_new_chat",headers=headers)
        create_new_chat_response_json = create_new_chat_response.json()

        assert create_new_chat_response.status_code == 201
        assert "conversation_id" in create_new_chat_response_json






@pytest.mark.asyncio
async def test_stream_chatbot_response():
    '''
        Test that chatbot gives appropriate response
    
    '''

    with TestClient(app=app) as client:

        user_query = "what is shoulder adduction?"

        #example chats - mimicks the structure of chats extracted from the database
        test_chat_history = [
        {"type":"bot","message":"Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.",'timestamp': '2026-01-01 11:37:11.409816'}]
                            
        test_client_form = ClientForm(  
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

        print(user_query)


        # send a sample
        with client.stream("POST","/chat",json={
            "user_query": user_query,
            "chat_history": test_chat_history,
            "client_form": test_client_form.model_dump()
            }) as response:

            chunks = list(response.iter_text())

            

        print(chunks)
        assert all(isinstance(chunk,str) for chunk in chunks)



