import os
from dotenv import load_dotenv

#get environment variables from dotenv file
load_dotenv()

MONGO_DB_CONNECTION_STRING = os.getenv("MONGO_DB_CONNECTION_STRING")

DATABASE_NAME = "trainwithtaku_web"
TEST_DATABASE_NAME = "trainwithtaku_test"

USER_ACCOUNTS_COLLECTION_NAME = "user_accounts"
TEST_USER_ACCOUNTS_COLLECTION_NAME = "user_accounts"

VECTOR_STORE_COLLECTION_NAME = "monyai_context_vectors"



MONGO_VECTOR_INDEX_NAME = "VectorSearchChatbot"
TEST_MONGO_VECTOR_INDEX_NAME = "VectorSearchTest"

CHAT_COLLECTION_NAME= "monyai_chats"
TEST_CHAT_COLLECTION_NAME= "monyai_chats"

TOP_K = 5



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBEDDING_MODEL_NAME = "text-embedding-3-large"

LLM_VERSION = "gpt-4o-mini"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
TOKEN_BLACKLIST_COLLECTION_NAME = "token_blacklist"

# Test credentials for integration testing
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD")
TEST_CONVERSATION_ID = os.getenv("TEST_CONVERSATION_ID")

