from src.config import EMBEDDING_MODEL_NAME, OPENAI_API_KEY
from langchain.embeddings import OpenAIEmbeddings

def get_embedding_model() -> OpenAIEmbeddings:
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