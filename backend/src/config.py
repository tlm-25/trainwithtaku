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
