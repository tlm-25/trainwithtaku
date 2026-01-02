from pymongo.asynchronous.collection import AsyncCollection
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.runnables import RunnablePassthrough, RunnableParallel,RunnableLambda
from langchain_mongodb import MongoDBAtlasVectorSearch
# from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from src.embeddings import get_embedding_model
from src.config import TOP_K
# async def get_retriever
# retriever = MongoDBAtlasVectorSearch(collection=).as_retriever()

# Tutorial: https://www.youtube.com/watch?v=JEBDfGqrAUA


async def mongo_db_vector_search(query:str,vector_store_collection:AsyncCollection,mongo_index_name:str):
    '''

    :param: query: User input to the chatbot
    :type query: str

    :param: vector_store_collection: the collection containing the vectors
    :type vector_store_collection: AsyncCollection

    :param: mongo_index_name: Name of the index created in MongoDB
    :type mongo_index_name: str

    
    
    
    '''
    
    
    EMBEDDING_MODEL = await get_embedding_model()
    query_vector = await EMBEDDING_MODEL.aembed_query(text=query)
    
    #settings for the vector search
    search_settings = {
        "$vectorSearch":{
            "queryVector":query_vector,
            "path":"embedding",
            "numCandidates":100,
            "limit":TOP_K,
            "index":mongo_index_name,

        }
    }

    retrieval_results = await vector_store_collection.aggregate([
        search_settings
    ])

    retrieved_documents_list = []
    async for document in retrieval_results:
        retrieved_documents_list.append(document)


    return retrieved_documents_list

