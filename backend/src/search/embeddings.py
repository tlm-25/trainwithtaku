from src.config import APP_CONFIG
EMBEDDING_MODEL_NAME = APP_CONFIG.chatbot.embedding_model_name
OPENAI_API_KEY = APP_CONFIG.chatbot.openai_api_key
from langchain_openai import OpenAIEmbeddings

async def get_embedding_model() -> OpenAIEmbeddings:
    '''
        Get the embedding model for generating text embeddings
        
        :return: embedding model
        :rtype: OpenAIEmbeddings
    '''
    embedding_model = OpenAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        openai_api_key=OPENAI_API_KEY
    )
    return embedding_model