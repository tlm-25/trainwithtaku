import pytest
from fastapi.testclient import TestClient
from src.app_setup import create_app
from pymongo import AsyncMongoClient
from src.database.connection import create_or_get_database
from src.config import APP_CONFIG
import logging
MONGO_DB_CONNECTION_STRING = APP_CONFIG.database.mongo_db_connection_string.get_secret_value()
TEST_DATABASE_NAME  = APP_CONFIG.database.test_database_name
USER_ACCOUNTS_COLLECTION_NAME = APP_CONFIG.database.user_accounts_collection_name
TEST_USER_EMAIL = APP_CONFIG.email.test_user_email
TEST_USER_PASSWORD = APP_CONFIG.email.test_user_password.get_secret_value()
PASSWORD_RESET_COLLECTION_NAME = APP_CONFIG.database.password_reset_collection_name
PASSWORD_RESET_MINUTES = APP_CONFIG.auth.reset_password_link_expire_minutes


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


test_app = create_app()
# disable rate limiting so that it does not affect testing functionality unless 
#... only skip this line in tests if explicity testing rate limiting
test_app.state.user_based_rate_limiter.enabled = False
test_app.state.ip_rate_limiter.enabled = False
test_app.dependency_overrides[create_or_get_database] = create_or_get_test_database
client = TestClient(app=test_app)

@pytest.fixture
def test_blog_data():
    return {
        "article_id": 1,
        "title": "Test Blog Title",
        "article_text": "This is a test blog article.",
        "headline_image_file": None  # No image for this test
    }

@pytest.fixture
def test_blog_data_with_image():
    return {
        "article_id": 2,
        "title": "Test Blog Title with Image",
        "article_text": "This is a test blog article with an image.",
        "headline_image_file": "test_image.jpg"  # Assuming this file exists in the test directory
    }



@pytest.mark.asyncio
@pytest.mark.mongodb
async def test_upload_blog_without_image(test_blog_data):
    with TestClient(app=test_app) as client:
        response = client.post(
            "/api/upload_blog",
            data={
                "article_id": test_blog_data["article_id"],
                "title": test_blog_data["title"],
            "article_text": test_blog_data["article_text"]
        }
    )
    assert response.status_code == 200
    logging.info(response.json())
    assert response.json()["message"].lower() == "blog uploaded successfully"
    # delete the uploaded blog from the test database
    async with AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING,serverSelectionTimeoutMS=10000) as mongo_client:
        database = mongo_client[TEST_DATABASE_NAME]
        blog_collection_name = APP_CONFIG.blogs.blog_collection_name
        data =  await database[blog_collection_name].find_one({"article_id":1})
        logging.info(f"data:{data}")
        assert data["article_id"] == 1
        await database[blog_collection_name].delete_one({"article_id": 1})

