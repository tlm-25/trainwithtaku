import os
from dotenv import load_dotenv

#get environment variables from dotenv file
load_dotenv()

MONGO_DB_CONNECTION_STRING = os.getenv("MONGO_DB_CONNECTION_STRING")

DATABASE_NAME = "trainwithtaku_web"

TEST_DATABASE_NAME = "trainwithtaku_test"

USER_ACCOUNTS_COLLECTION_NAME = "user_accounts"

TEST_USER_ACCOUNTS_COLLECTION_NAME = "user_accounts"