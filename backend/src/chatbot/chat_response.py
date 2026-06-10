from src.search.retrieval import CustomAsyncMongoDBAtlasRetriever, create_training_retrieval_query_from_form_and_user_query, format_documents_for_prompt
from src.chatbot.chat_history import convert_chat_history_to_langchain_format
from src.config import APP_CONFIG
import json
import logging
LLM_VERSION = APP_CONFIG.chatbot.llm_version
OPENAI_API_KEY = APP_CONFIG.chatbot.openai_api_key.get_secret_value()
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name
MONGO_VECTOR_INDEX_NAME = APP_CONFIG.database.mongo_vector_index_name
CHAT_COLLECTION_NAME = APP_CONFIG.database.chat_collection_name

from src.schemas import ClientForm, ChatMessage
from src.prompts import TRAINING_PROGRAM_PROMPT_CONCISE

from langchain_core.prompts.chat import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.messages import  HumanMessage
from pymongo.asynchronous.collection import AsyncCollection

from datetime import datetime


CHAT_MODEL = ChatOpenAI(
    model=LLM_VERSION,
    openai_api_key=OPENAI_API_KEY,
    temperature=0

)

# General LLM Wrapper Class 


TRAINING_RETRIEVAL_QUERY_TEMPLATE = """

USER QUERY
- Query: {user_query}

CLIENT DATA 
- Activity Level: {current_activity_level} 
- Occupation: {current_occupation}
- Daily step count: {current_average_steps_per_day}
- Main fitness goal: {primary_fitness_goal}
- Training days per week: {days_available_to_train_per_week}
- Training location: {preferred_location}
- Training equipment available: {equipment_available}
- Injury or pain history:{injuries}
"""


# PROMPT = ChatPromptTemplate.from_template(template=TRAINING_PROGRAM_PROMPT_CONCISE)

# PROMPT = ChatPromptTemplate.from_messages([SystemMessage(content=TRAINING_PROGRAM_PROMPT_CONCISE), MessagesPlaceholder(variable_name="chat_history"), HumanMessagePromptTemplate.from_template(template="{query}")])



# create chain for chatbot giving general responses and specialised for training program





async def stream_chatbot_response(user_query:str,chat_history:list[dict],vector_store_collection:AsyncCollection,conversation_collection:AsyncCollection,conversation_id:str,client_form:ClientForm|None=None):
    '''
    Stream chatbot response based on user query, relevant client form data, and chat history

    :param user_query: User's query
    :type user_query: str
    :param client_form: Client form data
    :type client_form: ClientForm
    :param chat_history: Chat history
    :type chat_history: list[dict]
    :return: Streamed chatbot response
    :rtype: AsyncGenerator[str]
    '''
    if client_form is None or not client_form:
        client_form_text = ""
    
    else:
        #get info from client form
        client_form_dict = client_form.model_dump()
        client_form_text = "FORM INFO:"+ "\n".join(f"{k}: {v}" for k, v in client_form_dict.items())
    

    #retrieve relevant documents based on use query and client form data
    retrieval_query = create_training_retrieval_query_from_form_and_user_query(retrieval_query_template=TRAINING_RETRIEVAL_QUERY_TEMPLATE,client_form=client_form,user_query=user_query)

    async_mongodb_retriever = CustomAsyncMongoDBAtlasRetriever(vector_store_collection=vector_store_collection,mongo_index_name=MONGO_VECTOR_INDEX_NAME)
    #get the relevant documents
    retrieved_documents = await async_mongodb_retriever.ainvoke(input=retrieval_query)

    print(retrieved_documents)
    logging.info(retrieved_documents)

    references = [doc.page_content  for doc in retrieved_documents]

    
    references_json = json.dumps(references)

    string_formatted_documents = format_documents_for_prompt(documents=retrieved_documents)
    
    logging.info(f"Retrieved Documents: {string_formatted_documents}")
    

    chat_prompt = ChatPromptTemplate.from_messages([("system",TRAINING_PROGRAM_PROMPT_CONCISE)])

    # fill in the {retrieved_docs} placeholder in system prompt with the retrieved documents
    messages = chat_prompt.format_messages(retrieved_docs=string_formatted_documents,client_info=client_form_text)

    #convert chat history to langchain format 
    langchain_formatted_chat_history = await convert_chat_history_to_langchain_format(chat_history=chat_history)

    #add the chat history as context
    messages.extend(langchain_formatted_chat_history)
    
    

    

    # add information from client form to context
    messages.append(HumanMessage(content=client_form_text))


    messages.append(HumanMessage(content=user_query))
    

    response = CHAT_MODEL.astream(messages)

    # store the contents of the message as it is streamed so that we can add it to the database
    accumulated_text = ""
    async for chunk in response:
        text_chunk = chunk.content
        accumulated_text+=chunk.content
        yield text_chunk
    logging.info(f" String formatted docs: {string_formatted_documents}")
    # use __REFS__ as a reference for the frontend to be able to distinguish references text from the message text 
    yield f"__REFS__{string_formatted_documents}"
     # store the chatbot response in the database once generated 

    final_generated_message = ChatMessage(message=accumulated_text,timestamp=str(datetime.now()),type='bot',reference_docs=string_formatted_documents)
   
    add_message_to_db = await conversation_collection.update_one(
            {"conversation_id": conversation_id},
            {"$push": {"messages": final_generated_message.model_dump()}}
            )

    #  add_message_to_db = await conversation_container.patch_item(item = cosmos_id, partition_key=conversation_id,patch_operations =[{ "op": "add", "path": "/messages/-", "value": final_generated_message_dict}])


        
