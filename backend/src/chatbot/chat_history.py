
from pymongo.asynchronous.collection import AsyncCollection

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


async def get_specific_stored_user_chat(conversation_id:str,conversations_collection:AsyncCollection)->dict:
    '''
        Retrieve a specific stored conversation for a given conversation ID from the database - get the list of messages in the conversation

        :param conversation_id: Unique identifier for the conversation
        :type conversation_id: str
        :param conversations_collection: MongoDB collection storing conversations
        :type conversations_collection: pymongo.asynchronous.collection.AsyncCollection
        :return: Conversation associated with the given conversation ID
        :rtype: dict
    '''


    
    # get all the messages stored for a specific conversation for specific user - using cursor to so only a portion of chats loaded at a time - set projection to exclude _id field (avoid errors when sending to endpoint) - JSONREsponse can't serialize ObjectId type
    chat_info =  await conversations_collection.find_one({"conversation_id":conversation_id},projection={"_id":False})
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


async def convert_chat_history_to_langchain_format(chat_history:list[dict])->list[HumanMessage | AIMessage | SystemMessage]:
    '''
        Retrieve previous chat history as dict and return list of langchain formatted message objects 
    '''
    langchain_formatted_chat_history = []
    for message in chat_history:
        if message["type"] == "user":
            langchain_formatted_chat_history.append(HumanMessage(content=message["message"]))
        elif message["type"] == "bot":
            langchain_formatted_chat_history.append(AIMessage(content=message["message"]))
        elif message["type"] == "system":
            langchain_formatted_chat_history.append(SystemMessage(content=message["message"]))
    return langchain_formatted_chat_history