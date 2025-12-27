
from src.main import app
from src.schemas import UserSignUpForm
from src.database.connection import create_or_get_database
from src.config import TEST_DATABASE_NAME, MONGO_DB_CONNECTION_STRING

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from fastapi.testclient import TestClient
import pytest, pytest_asyncio

from datetime import datetime 
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



client = TestClient(app=app)

app.dependency_overrides[create_or_get_database] = create_or_get_test_database



     
@pytest.mark.asyncio
async def test_successful_user_sign_up():

    with TestClient(app=app) as client:
        email = f"test{str(uuid.uuid4())}@gmail.com"
        password = "Codeword1!!"
        confirm_password = password
        user_type = "trainee"
        test_user_details = UserSignUpForm(email=email,password=password,confirm_password=confirm_password,user_type=user_type)
        test_user_details_mock_json = test_user_details.model_dump()
        response =  client.post(url="/add_user",json=test_user_details_mock_json)

        assert response.status_code == 200
        assert  isinstance(response.json()["message"],str)

@pytest.mark.asyncio
async def test_invalid_email_format_user_sign_up():
    '''
        Testing response to incorrectly formatted email
    '''


    with TestClient(app=app) as client:
        email = f"test{str(uuid.uuid4())}gmail.com"
        password = "Codeword1!!"
        confirm_password = password
        user_type = "trainee"
        test_user_details = UserSignUpForm(email=email,password=password,confirm_password=confirm_password,user_type=user_type)
        test_user_details_mock_json = test_user_details.model_dump()
        response =  client.post(url="/add_user",json=test_user_details_mock_json)

        assert response.status_code == 422
        assert  isinstance(response.json()["message"],str)
        assert "email" in response.json()["message"].lower() and "invalid" in  response.json()["message"].lower()

@pytest.mark.asyncio
async def test_email_already_exists():
    '''
    Test that we can correctly identify that an email is already in use - (created a document in collection to test). This test that assumes an email
    with the address 'existing_email@gmail.com' is in the 'user_accounts' collection within the test database
    '''

    existing_email = "existing_email@gmail.com"
    password = "Codeword1!!"
    confirm_password = password
    user_type = "trainee"
    test_user_details = UserSignUpForm(email=existing_email,password=password,confirm_password=confirm_password,user_type=user_type)
    test_user_details_mock_json = test_user_details.model_dump()
    response =  client.post(url="/add_user",json=test_user_details_mock_json)
    assert response.status_code == 422
    assert "already in use" in response.json()["message"].lower()
    



    





