import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from slowapi import Limiter

from src.config import APP_CONFIG
from src.rate_limiter import get_real_ip
import redis
import uuid
import src.routers.auth as auth_router
from src.main import app
from src.rate_limiter import limiter
import logging
TEST_USER_EMAIL = APP_CONFIG.email.test_user_email
TEST_USER_PASSWORD = APP_CONFIG.email.test_user_password.get_secret_value()

REDIS_CONNECTION_STRING = APP_CONFIG.redis_config.redis_connection_string.get_secret_value()
TEST_REDIS_CONNECTION_STRING = APP_CONFIG.redis_config.test_redis_connection_string.get_secret_value()




@pytest.fixture
def setup_test_limiter():

    test_limiter = Limiter(key_func=get_real_ip, storage_uri=TEST_REDIS_CONNECTION_STRING)

    # slowapi stores the limiter here — this is what's checked at request time
    original_limiter = app.state.limiter
    app.state.limiter = test_limiter

    # also swap the module ref for completeness
    original_router_limiter = auth_router.limiter
    auth_router.limiter = test_limiter

    yield

    app.state.limiter = original_limiter
    auth_router.limiter = original_router_limiter


@pytest.fixture
def flush_test_database(setup_test_limiter):
    '''Connect to the test redis database to test rate limiting'''

    redis_client = redis.from_url(url=TEST_REDIS_CONNECTION_STRING)
    print(redis_client.keys("*"))
    #clear test database from previous tests 
    redis_client.flushdb()
    print(redis_client.keys("*"))
    logging.info("test redis database flushed")
    print("flushed")
    yield
    # clear database after test 
    redis_client.flushdb()
    print(redis_client.keys("*"))
    print("flushed")




@pytest.mark.asyncio
@pytest.mark.slow
async def test_incorrect_login_rate_limit(flush_test_database):
    '''
        Simulate brute force attack where somebody tried to guess password 
        Return 401 error for the first 10
        When the 11th attempt is made within a minute, a 429 error should be returned 
    '''

    with TestClient(app=app) as client:
        # first 10 login attemps (incorrect password)
        for i in range(0,10):

            print (f"attempt {i}")
            

            password_guess = str(uuid.uuid4())
            response = client.post("/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":password_guess})
         
            assert response.status_code == 401

        #ensure a 429 error code is returned with rate limit in reached
        response = client.post("/login_with_access_token",data={"username":TEST_USER_EMAIL,"password":password_guess})
        assert response.status_code== 429
    





