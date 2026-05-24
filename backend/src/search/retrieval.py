from pymongo.asynchronous.collection import AsyncCollection
from langchain_core.retrievers import BaseRetriever
from langchain.schema import Document
from typing_extensions import Self, TypedDict, override

# from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from src.search.embeddings import get_embedding_model

from src.config import APP_CONFIG
TOP_K = APP_CONFIG.chatbot.top_k
from src.schemas import ClientForm
# async def get_retriever
# retriever = MongoDBAtlasVectorSearch(collection=).as_retriever()





def create_training_retrieval_query_from_form_and_user_query(retrieval_query_template:str,user_query:str,client_form:ClientForm|None=None,)->str:
    '''
    Create a retrieval query based on the client form data 

    :param client_form: Client form data
    :type client_form: ClientForm

    :return: Retrieval query string
    :rtype: str
    '''

    if not client_form or client_form is None:
        return retrieval_query_template.format(
            user_query=user_query,
            current_activity_level= "N/A",
            current_occupation = "N/A",
            current_average_steps_per_day = "N/A",
            primary_fitness_goal = "N/A",
            days_available_to_train_per_week = "N/A",
            preferred_location = "N/A",
            equipment_available = "N/A",
            injuries = "N/A"
            )


    client_form_dict = client_form.model_dump()
    return retrieval_query_template.format(
            user_query=user_query,
            current_activity_level= client_form_dict.get("current_activity_level"),
            current_occupation = client_form_dict.get("current_occupation"),
            current_average_steps_per_day = client_form_dict.get("current_average_steps_per_day"),
            primary_fitness_goal = client_form_dict.get("primary_fitness_goal"),
            days_available_to_train_per_week = client_form_dict.get("days_available_to_train_per_week"),
            preferred_location = client_form_dict.get("preferred_location"),
            equipment_available = client_form_dict.get("equipment_available"),
            injuries = client_form_dict.get("injuries")
            )





# Tutorial: https://www.youtube.com/watch?v=JEBDfGqrAUA

async def mongo_db_vector_search(query:str,vector_store_collection:AsyncCollection,mongo_index_name:str) ->list[Document]:
    '''
    Perform vector search in MongoDB collection to retriever relevant documents based on user query 

    Using custom function instead of default langchain MongoDBAtlasVectorSearch due to compatibality issues with AsyncCollection (annoyingly, langchain's MongoDBAtlasVectorSearch class only works reliably with synchronous collections) 
    
    :param: query: User input to the chatbot
    :type query: str

    :param: vector_store_collection: the collection containing the vectors
    :type vector_store_collection: AsyncCollection

    :param: mongo_index_name: Name of the index created in MongoDB
    :type mongo_index_name: str

    :return: List of retrieved documents
    :rtype: list

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
        # put into Document object with 'page_content' property since langchain is expecting
        retrieved_documents_list.append(Document(page_content=document["content"]))
    return retrieved_documents_list

def format_documents_for_prompt(documents:list[Document])->str:
    '''
    Take a lists of Document objects and format them into a string, to feed into the LLM
    
    :param documents: list of documents
    :type documents: list[Document]
    :return: documents formatted as a single string
    :rtype: str
    '''

    for i in range(len(documents)):
        documents[i].page_content = f"Source {i+1}: " + documents[i].page_content.strip() + "\n"

    documents_string = " ".join([doc.page_content for doc in documents])

    return " ".join([doc.page_content for doc in documents])



            


class CustomAsyncMongoDBAtlasRetriever(BaseRetriever):
    '''
    Making custom async retriever inheriting from langchain baseretriever object to allow for easier integration when setting up langchain chain

    Langchain Documentation https://reference.langchain.com/python/langchain_core/retrievers/#langchain_core.retrievers.BaseRetriever
    '''
    # pydantic style type hinting
    vector_store_collection: AsyncCollection
    mongo_index_name: str

    # raise and error if user tries to call synchronous version of get_relevant_documents - this is an async only class 
    def _get_relevant_documents(self, query: str):
        raise NotImplementedError("This class is async only - please user aget_relevant_documents instead")
    
    # raise and error if user tries to call synchronous version of get_relevant_documents - this is an async only class 
    @override
    def invoke(self, query: str):
        raise NotImplementedError("This class is async only - please user ainvoke instead")
    
    # raise and error if user tries to call synchronous version of get_relevant_documents - this is an async only class 
    def _get_relevant_documents(self, query: str):
        raise NotImplementedError("This class is async only - please user aget_relevant_documents instead")
    


    # override _aget_relevant_documents method from baseretriever class and perform vector search using the custom mongo db functionality -
    @override
    async def _aget_relevant_documents(self, query:str):
        documents = await mongo_db_vector_search(query = query, vector_store_collection=self.vector_store_collection,mongo_index_name=self.mongo_index_name)
        return documents
    



