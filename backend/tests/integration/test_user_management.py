
from src.main import app
from src.schemas import UserSignUpForm, UserLoginForm
from src.database.connection import create_or_get_database
from src.database.user_management.utils import check_if_email_already_in_use
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
async def test_email_already_exists_sign_up():
    '''
    Test that we can correctly identify that an email is already in use - (created a document in collection to test). This test that assumes an email
    with the address 'existing_email@gmail.com' is in the 'user_accounts' collection within the test database
    '''
    with TestClient(app=app) as client:
        existing_email = "existing_email@gmail.com"
        password = "Codeword1!!"
        confirm_password = password
        user_type = "trainee"
        test_user_details = UserSignUpForm(email=existing_email,password=password,confirm_password=confirm_password,user_type=user_type)
        test_user_details_mock_json = test_user_details.model_dump()
        response =  client.post(url="/add_user",json=test_user_details_mock_json)
        assert response.status_code == 409
        assert "already in use" in response.json()["message"].lower()
        


@pytest.mark.asyncio
async def test_successful_login_with_access_token():
    '''
    Test that a JWT token is generated on successful login and that the token has the correct structure
    '''
    with TestClient(app=app) as client:
        existing_email = "existing_email@gmail.com"
        password = "Codeword1!!"

        response = client.post(url="/login_with_access_token",data={"username":existing_email,"password":password})
        response_json =response.json()
        assert response.status_code == 200
        assert "access_token" in response_json
        assert "token_type" in response_json


@pytest.mark.asyncio
async def test_login_incorrect_email():
    '''
    Test edge case of incorrect email (username)
    ''' 
    with TestClient(app=app) as client:
        # incorrect email for login - does not exist in the test database
        existing_email = "exist_email@gmail.com"
        password = "Codeword1!!"
        response = client.post(url="/login_with_access_token",data={"username":existing_email,"password":password})
        response_json =response.json()
        assert response.status_code == 401
        assert "incorrect" in response_json["message"].lower()

@pytest.mark.asyncio
async def test_login_incorrect_password():
    '''
    Test edge case of incorrect password in login

    ''' 
    with TestClient(app=app) as client:

        existing_email = "existing_email@gmail.com"
        #incorrect password for the user in the test database
        password = "Codword1!"
        response = client.post(url="/login_with_access_token",data={"username":existing_email,"password":password})
        response_json =response.json()
        assert response.status_code == 401
        assert "incorrect" in response_json["message"].lower()

@pytest.mark.asyncio
async def test_get_current_user():
    '''
    Test that the current user is correctly retrieved from the database
    '''
    with TestClient(app=app) as client:
        existing_email = "existing_email@gmail.com"
        password = "Codeword1!!"

        # First, login to get a valid access token
        login_response = client.post(url="/login_with_access_token",data={"username":existing_email,"password":password})
        login_response_json = login_response.json()

        # Use the access token to get current user info
        headers = {"Authorization": f"Bearer {login_response_json['access_token']}"}
        current_user_response = client.post(url="/get_current_user", headers=headers)
        current_user_response_json  = current_user_response.json()
        assert current_user_response.status_code == 200
        assert "user_email" in current_user_response_json
        print(current_user_response_json)
        assert current_user_response_json["user_email"] == existing_email
