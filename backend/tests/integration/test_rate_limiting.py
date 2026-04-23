import pytest
from fastapi.testclient import TestClient


from src.config import APP_CONFIG

import redis
import uuid

# from src.rate_limiter import limiter

from src.app_setup import create_app
import logging

TEST_USER_EMAIL = APP_CONFIG.email.test_user_email
TEST_USER_PASSWORD = APP_CONFIG.email.test_user_password.get_secret_value()

REDIS_CONNECTION_STRING = APP_CONFIG.redis_config.redis_connection_string.get_secret_value()
TEST_REDIS_CONNECTION_STRING = None



@pytest.fixture
def test_client():

    # create test app
    test_app =  create_app(redis_rl_storage_uri=TEST_REDIS_CONNECTION_STRING)
    # create test client
    test_client = TestClient(app=test_app)

    logging.info("Created test database")
   
    yield test_client

    # No flush 

    logging.info("Flushed test database")


@pytest.mark.asyncio
@pytest.mark.slow
async def test_incorrect_login_rate_limit(test_client):
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
    





