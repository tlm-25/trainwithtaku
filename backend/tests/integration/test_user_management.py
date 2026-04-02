
from src.main import app
from src.schemas import UserSignUpForm, UserResetPasswordForm
from src.database.connection import create_or_get_database
from src.database.user_management.utils import check_if_email_already_in_use
from src.database.user_management.password import hash_password, is_correct_password
from src.config import APP_CONFIG

MONGO_DB_CONNECTION_STRING = APP_CONFIG.database.mongo_db_connection_string
TEST_DATABASE_NAME  = APP_CONFIG.database.test_database_name
USER_ACCOUNTS_COLLECTION_NAME = APP_CONFIG.database.user_accounts_collection_name
TEST_USER_EMAIL = APP_CONFIG.email.test_user_email
TEST_USER_PASSWORD = APP_CONFIG.email.test_user_password
PASSWORD_RESET_COLLECTION_NAME = APP_CONFIG.database.password_reset_collection_name
PASSWORD_RESET_MINUTES = APP_CONFIG.auth.reset_password_link_expire_minutes


from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
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
    
    except RuntimeError as e:
          raise RuntimeError(f"failed to connect to database {TEST_DATABASE_NAME}: {e}")



client = TestClient(app=app)

app.dependency_overrides[create_or_get_database] = create_or_get_test_database



     
@pytest.mark.asyncio
async def test_successful_user_sign_up():
    '''
        Test successful user sign up with valid email and password'''

    with TestClient(app=app) as client:
        email = f"test{str(uuid.uuid4())}@gmail.com"
        user_type = "trainee"
        test_user_details = UserSignUpForm(email=email,password=TEST_USER_PASSWORD,confirm_password=TEST_USER_PASSWORD,user_type=user_type)
        test_user_details_mock_json = test_user_details.model_dump()
        response =  client.post(url="/add_user",json=test_user_details_mock_json)

        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_password_confirm_pw_mismatch():
    '''
        Test scenario when password and confirm password fields are mismatched in user sign up'''

    with TestClient(app=app) as client:
        email = f"test{str(uuid.uuid4())}@gmail.com"
        user_type = "trainee"
        test_user_details = UserSignUpForm(email=email,password=TEST_USER_PASSWORD,confirm_password="Password11!",user_type=user_type)
        test_user_details_mock_json = test_user_details.model_dump()
        response =  client.post(url="/add_user",json=test_user_details_mock_json)

        assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_email_format_user_sign_up():
    '''
        Testing response to incorrectly formatted email
    '''


    with TestClient(app=app) as client:
        email = f"test{str(uuid.uuid4())}gmail.com"
        user_type = "trainee"
        test_user_details = UserSignUpForm(email=email,password=TEST_USER_PASSWORD,confirm_password=TEST_USER_PASSWORD,user_type=user_type)
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
        user_type = "trainee"
        test_user_details = UserSignUpForm(email=TEST_USER_EMAIL,password=TEST_USER_PASSWORD,confirm_password=TEST_USER_PASSWORD,user_type=user_type)
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
        existing_email = TEST_USER_EMAIL
        password = TEST_USER_PASSWORD

        response = client.post(url="/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":TEST_USER_PASSWORD})
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
        incorrect_email = "exist_email@gmail.com"
        response = client.post(url="/login_with_access_token",data={"username":incorrect_email,"password":TEST_USER_PASSWORD})
        response_json =response.json()
        assert response.status_code == 401
        assert "incorrect" in response_json["message"].lower()

@pytest.mark.asyncio
async def test_login_incorrect_password():
    '''
    Test edge case of incorrect password in login

    ''' 
    with TestClient(app=app) as client:
        #incorrect password for the user in the test database
        incorrect_password = "incorrect_password"
        response = client.post(url="/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":incorrect_password})
        response_json =response.json()
        assert response.status_code == 401
        assert "incorrect" in response_json["message"].lower()

@pytest.mark.asyncio
async def test_get_current_user():
    '''
    Test that the current user is correctly retrieved from the database
    '''
    with TestClient(app=app) as client:
        # First, login to get a valid access token
        login_response = client.post(url="/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":TEST_USER_PASSWORD})
        login_response_json = login_response.json()

        # Use the access token to get current user info
        headers = {"Authorization": f"Bearer {login_response_json['access_token']}"}
        current_user_response = client.get(url="/me", headers=headers)
        current_user_response_json  = current_user_response.json()
        assert current_user_response.status_code == 200
        assert "user_email" in current_user_response_json
        print(current_user_response_json)
        assert current_user_response_json["user_email"] == TEST_USER_EMAIL

@pytest.mark.asyncio
async def test_new_refresh_token_is_useable():
    '''
    Test that the new access token returned by /refresh actually works on a
    protected endpoint (/me).
    '''
    with TestClient(app=app) as client:
        
        login_response = client.post(
            url="/login_with_access_token",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )

        refresh_token_cookie = login_response.cookies.get("refresh_token")
        assert refresh_token_cookie is not None, "Refresh token must be set on login"

    
        # Note-  refresh token cookie automatically inclided in this request by testclient, simulating how a browser would send the cookie
        refresh_response = client.post(url="/refresh")
        new_access_token = refresh_response.json()["access_token"]
 
        me_response = client.get(
            url="/me",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["user_email"] == TEST_USER_EMAIL

@pytest.mark.asyncio
async def test_refresh_without_cookie_returns_401():
    '''
    Test that /refresh returns 401 when no refresh token cookie is present.
    '''
    with TestClient(app=app) as client:
        # Deliberately do not login — no cookie will be set
        refresh_response = client.post(url="/refresh")
        assert refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_invalid_cookie_returns_401():
    '''
    Test that /refresh returns 401 when the cookie contains a tampered or
    invalid token string.
    '''
    with TestClient(app=app) as client:
        

        client.cookies.set("refresh_token", "this.is.not.a.valid.jwt")
        refresh_response = client.post(url="/refresh")
        assert refresh_response.status_code == 401

# TODO - logout tests

@pytest.mark.asyncio
async def test_logout_twice_still_returns_200():
    '''
    Test that calling /logout twice does not error — idempotent logout.
    Test that it allows logout even if refresh token already blacklisted
    '''
    with TestClient(app=app) as client:
        client.post(
            url="/login_with_access_token",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
 
        first_logout = client.post(url="/logout")
        assert first_logout.status_code == 200
 
        second_logout = client.post(url="/logout")
        assert second_logout.status_code == 200

@pytest.mark.asyncio
async def test_logout_without_cookie_still_returns_200():
    '''
    Test that /logout returns 200 even when no refresh token cookie is present
    — logout should never error, regardless of cookie state.
    '''
    with TestClient(app=app) as client:
        # Deliberately do not login
        logout_response = client.post(url="/logout")
        assert logout_response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_success():

    '''
    Test that password successfully resets 
    
    '''

    try:

        # create dummy user 
        test_database = await create_or_get_test_database().__anext__()
        users_collection = test_database[USER_ACCOUNTS_COLLECTION_NAME]

        email = f"test{str(uuid.uuid4())}@gmail.com"
        user_type = "trainee"
        test_user_details = UserSignUpForm(email=email,password=TEST_USER_PASSWORD,confirm_password=TEST_USER_PASSWORD,user_type=user_type)
        test_user_details_mock_json = test_user_details.model_dump()
        response =  client.post(url="/add_user",json=test_user_details_mock_json)

        #store user password hash for assert statement later
        test_user_password_hash = hash_password(password_string=TEST_USER_PASSWORD)

        dummy_token = str(uuid.uuid4())
        # create user account 

        dummy_password_new = TEST_USER_PASSWORD+"new"

        
        reset_collection = test_database[PASSWORD_RESET_COLLECTION_NAME]

        await reset_collection.insert_one({
            "token": dummy_token,
            "email": email,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_MINUTES)
        })

        reset_password_form = UserResetPasswordForm(new_password=dummy_password_new,confirm_new_password=dummy_password_new,token=dummy_token).model_dump()
        response = client.post("/reset_password",json=reset_password_form)
        user_updated = await users_collection.find_one(filter={"email": email}, projection={"_id": True,"password":True})
        # bcrypt is non-deterministic so use is_correct_password instead of comparing hashes directly
        assert is_correct_password(password_string=dummy_password_new, hashed_password=user_updated["password"])
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()
    finally:
        await users_collection.delete_one(filter={"email":email})
        await reset_collection.delete_one(filter={"token":dummy_token})








@pytest.mark.asyncio
async def test_expired_reset_password_token():
    '''

        Test that password reset properly handles an expired password
    
    
    '''

    try:
        with TestClient(app=app) as client:
            dummy_token  =str(uuid.uuid4())
            dummy_password = "dummy_password"

            
            test_database = await create_or_get_test_database().__anext__()
            reset_collection = test_database[PASSWORD_RESET_COLLECTION_NAME]
            await reset_collection.insert_one({
                "token": dummy_token,
                "email": TEST_USER_EMAIL,
                # simulate expired token
                "expires_at": datetime.now(timezone.utc) - timedelta(minutes=1)
            })

            password_reset_request = UserResetPasswordForm(token=dummy_token,new_password=dummy_password,confirm_new_password=dummy_password)
            password_reset_request_json = password_reset_request.model_dump()
            response = client.post("/reset_password",json=password_reset_request_json)

            assert response.status_code == 401
            assert "expired" in response.json()["detail"].lower()

    


    finally:
        # clean up database after test (remove the dummy entry)
        await reset_collection.delete_one({"token": dummy_token})