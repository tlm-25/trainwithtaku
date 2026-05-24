
from pymongo.asynchronous.collection import AsyncCollection

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from src.schemas import ChatMessage
from src.config import APP_CONFIG as config
import json 
import logging 
from src.prompts import SUMMARISE_CHAT_HISTORY_PROMPT

CHAT_MODEL = ChatOpenAI(
    model=config.chatbot.llm_version,
    openai_api_key=config.chatbot.openai_api_key,
    temperature=0

)



async def _summarise_old_chat_history(chat_history:list[ChatMessage],max_number_of_messages:int)->str:
    '''
    :param chat_history: List of previous chat messages in the conversation

    :param max_number_of_messages: Maximum number of most recent messages to include in the context for the chatbot response generation - if chat history exceeds this number, the older messages will be summarised to save tokens but still preserve the information in the older messages
        
    '''
     # if chat history exceeds max to include in context, summarise the chat history and only include summary to save tokens 
    previous_n_messages = chat_history[:-max_number_of_messages]
    # convert to dict to send to prompt - easier to work with in the prompt and avoid issues with serialisation 
    previous_n_messages_dict = [message.model_dump() for message in previous_n_messages] 
    summary = await CHAT_MODEL.ainvoke([SystemMessage(content=SUMMARISE_CHAT_HISTORY_PROMPT.format(chat_history=json.dumps(previous_n_messages_dict)))])

    return summary.content



async def get_specific_stored_user_chat(current_user_email:str,conversation_id:str,conversations_collection:AsyncCollection)->dict:
    '''
        Retrieve a specific stored conversation for a given conversation ID from the database - get the list of messages in the conversation

        :param current_user: The email of the current user
        :type current_user: str
        :param conversation_id: Unique identifier for the conversation
        :type conversation_id: str
        :param conversations_collection: MongoDB collection storing conversations
        :type conversations_collection: pymongo.asynchronous.collection.AsyncCollection
        :return: Conversation associated with the given conversation ID
        :rtype: dict
    '''


    
    # get all the messages stored for a specific conversation for specific user - using cursor to so only a portion of chats loaded at a time - set projection to exclude _id field (avoid errors when sending to endpoint) - JSONREsponse can't serialize ObjectId type
    # also requiring the current user's email to ensure only retrieving conversations associated with the user - security measure to prevent unauthorized access to other users' conversations
    # The current_user will extracted from JWT token in the endpoint (via dependency injection) and passed to this function to ensure only retrieving conversations associated with the authenticated user
    chat_info =  await conversations_collection.find_one({"conversation_id":conversation_id,"email":current_user_email},projection={"_id":False})

    messages = chat_info["messages"]

    return messages


async def get_all_stored_user_chats(email:str,conversations_collection:AsyncCollection)->list[dict]:
    '''
        Retrieve all stored conversations for a given user email from the database

        :param email: User's email address
        :type email: str
        :param conversations_collection: MongoDB collection storing conversations
        :type conversations_collection: pymongo.asynchronous.collection.AsyncCollection
        :return: List of conversations associated with the user
        :rtype: list[dict]
    '''

    # get all the conversations stored for specific user - using cursor to so only a portion of chats loaded at a time - set projection to exclude _id field (avoid errors when sending to endpoint) - JSONREsponse can't serialize ObjectId type
    conversations_cursor = conversations_collection.find({"email":email},projection={"_id":False})
    conversations_list = []
    # loop through the cursor and append the conversations to a list
    async for conversation_record in conversations_cursor:
        conversations_list.append(conversation_record)

    return conversations_list


async def convert_chat_history_to_langchain_format(chat_history:list[ChatMessage])->list[HumanMessage | AIMessage | SystemMessage]:
    '''
        Retrieve previous chat history as dict and return list of langchain formatted message objects 
    '''
    langchain_formatted_chat_history = []

    if len(chat_history) >= config.chatbot.max_n_messages_in_history:
        #summarise any older messages that are not included in context to save tokens but still preserve info 
        summary = await _summarise_old_chat_history(chat_history=chat_history,max_number_of_messages=config.chatbot.max_n_messages_in_history)
           
        # # get the latest N messages to include in context (preserving the most recent context verbatim)
        latest_n_messages = chat_history[-config.chatbot.max_n_messages_in_history:]

        
        
        # add the summary of older messages to the chat history
        langchain_formatted_chat_history.append(SystemMessage(content=summary))

        for message in latest_n_messages:
            if message.type == "user":
                langchain_formatted_chat_history.append(HumanMessage(content=message.message))
            elif message.type == "bot":
                langchain_formatted_chat_history.append(AIMessage(content=message.message))
            elif message.type == "system":
                langchain_formatted_chat_history.append(SystemMessage(content=message.message))
        
        
    else:

        for message in chat_history:
            if message.type == "user":
                langchain_formatted_chat_history.append(HumanMessage(content=message.message))
            elif message.type == "bot":
                langchain_formatted_chat_history.append(AIMessage(content=message.message))
            elif message.type == "system":
                langchain_formatted_chat_history.append(SystemMessage(content=message.message))
        
    return langchain_formatted_chat_history