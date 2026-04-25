#custom modules 
from src.database.connection import create_or_get_database
from src.chatbot.chat_history import  get_specific_stored_user_chat, get_all_stored_user_chats
from src.chatbot.chat_response import stream_chatbot_response
from src.schemas import  ChatRequest, Conversation, ChatHistoryRequest, ChatMessage
from src.database.user_management.jwt_token import get_current_user

from pymongo.asynchronous.database import AsyncDatabase

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse,  JSONResponse


import uuid
import logging
from datetime import datetime
from slowapi import Limiter


from src.config import APP_CONFIG

CHAT_COLLECTION_NAME = APP_CONFIG.database.chat_collection_name
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name


router = APIRouter()

def create_chat_router(limiter:Limiter)->APIRouter:
    '''
    Factory function for creating chat router with an injected rate limiter.
    Allows different Redis backends to be used per environment (e.g. localhost/memory for tests, prod URI for production).

    :param limiter: Configured SlowAPI Limiter instance to use for rate limiting
    :type limiter: Limiter
    :return: APIRouter with all auth endpoints registered
    :rtype: APIRouter
    '''
    @router.post("/get_chat_history")
    async def get_chat_history(chat_request:ChatHistoryRequest,current_user:dict =Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database)):
        '''
            Retrieve stored conversation for a given user and conversation ID.

            :param request: Request body containing the conversation_id
            :type request: ChatHistoryRequest
            :param current_user: Authenticated user dict
            :type current_user: dict
            :param database: MongoDB database instance
            :type database: AsyncDatabase
            :return: Chat history for the conversation
            :rtype: JSONResponse
            '''
        
        try:
            
            main_database = database
            conversations_collection = main_database[CHAT_COLLECTION_NAME]
            current_user_email = current_user["email"]

            chat_history = await get_specific_stored_user_chat(current_user_email=current_user_email,conversation_id=chat_request.conversation_id,conversations_collection=conversations_collection)
            return JSONResponse(content=chat_history, status_code=200)
        except Exception as e:  
            message =   f"Failed to retrieve stored chats: {e}" 
            logging.error(message) 
            return JSONResponse(content={"message":message}, status_code=500)

    @router.post("/chat")
    @limiter.limit("10/minute")
    async def generate_chatbot_response(request:Request, chat_request:ChatRequest,database:AsyncDatabase=Depends(create_or_get_database),user:dict=Depends(get_current_user)):
        '''
        :param chat_request
        :type chat_request ChatRequest 
        
        '''

        main_database = database
        vector_store_collection = main_database[VECTOR_STORE_COLLECTION_NAME]
        conversation_collection = main_database[CHAT_COLLECTION_NAME]

        user_message = chat_request.user_message
        user_query = user_message.message
    

        #  INSERT USER QUERY INTO CONVERSATION
        add_message_to_db = await conversation_collection.update_one(
                {"conversation_id": chat_request.conversation_id},
                {"$push": {"messages": user_message.model_dump()}},
                upsert=True
                )
        print("saved message to db")


        response = StreamingResponse(stream_chatbot_response(user_query=user_query,chat_history=chat_request.chat_history,vector_store_collection=vector_store_collection,client_form=chat_request.client_form,conversation_id=chat_request.conversation_id,conversation_collection=conversation_collection))

        return response


        
    @router.post("/create_new_chat")
    async def create_new_chat(user:dict = Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database))->JSONResponse:
            '''
            Create a new converstion
            
                :param: user: The current user creating the chat
                :type user: str

                :param: create_new_chat
                :type  database: AsyncDatabase
            '''
            #generate random string to represent the chat id
            conversation_id = str(uuid.uuid4())

            #default greeting message for the chatbot
            now_datetime_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            default_message = {"type":"bot","message":"Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.",'timestamp': now_datetime_string}


            new_chat = Conversation(conversation_id=conversation_id,messages=[default_message],email=user["email"])

            new_chat_dict = new_chat.model_dump()

            conversations_collection = database[CHAT_COLLECTION_NAME]

            try:
                #insert new user to database
                inserted_conversation = await conversations_collection.insert_one(document=new_chat_dict)

                message = {"message":"successfully created new chat","conversation_id":conversation_id}
                logging.info(message)


                return JSONResponse(content=message,status_code=201)
            
            except Exception as e:

                message = {message:f"failed to create new chat: {e}",conversation_id:"n/a"}
                logging.info(message)


                return JSONResponse(content=message,status_code=409)






    @router.post("/clear_chat")
    async def clear_chat(chat:ChatHistoryRequest,database:AsyncDatabase=Depends(create_or_get_database),user:dict=Depends(get_current_user)):

        
        
        try: 
            main_database = database

            conversation_collection = main_database[CHAT_COLLECTION_NAME]

            conversation_id = chat.conversation_id
            #default chatbot message
            default_message = [ChatMessage(message="Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.", type="bot",timestamp=str(datetime.now())).model_dump()]

            # clear the chat and replace with default message
            clear_all_messages_from_convo = await conversation_collection.update_one(
            {"conversation_id": conversation_id,"email":user["email"]},
            {"$set": {"messages": default_message}})

                
            print("Successfully cleared chat")
            logging.info("Successfully cleared chat")

            return JSONResponse(content={"message":"successfully cleared chat"},status_code=200)
        except Exception as e:
            return JSONResponse(content={"message":"Failed to delete chat"},status_code=500)


    @router.delete("/delete_chat")
    async def delete_chat(chat:ChatHistoryRequest,database:AsyncDatabase=Depends(create_or_get_database),user:dict = Depends(get_current_user)):
        '''
            Delete chat from database
        
        '''
        main_database = database

        try:

            conversation_collection = main_database[CHAT_COLLECTION_NAME]
            conversation_id = chat.conversation_id

            # delete conversation with matching conversation ID and user email (only allow deletion if chat belong to the user)
            delete_conversation = await conversation_collection.delete_one({"conversation_id":conversation_id,"email":user["email"]})
            return JSONResponse(content={"message":"successfully deleted chat"},status_code=200)
        except Exception as e:
            return JSONResponse(content={"message":"Failed to delete chat"},status_code=500)
        

    @router.post("/get_stored_user_chats")
    async def get_stored_user_chats(user:dict=Depends(get_current_user),database:AsyncDatabase=Depends(create_or_get_database))->JSONResponse:
        '''
            Retrieve all stored conversations for a given user email from the database

            :param email: Retrieved user info
            :type email: dict
            :param database: MongoDB database instance
            :type database: pymongo.asynchronous.database.AsyncDatabase
            :return: List of conversations associated with the user
            :rtype: list[dict]
            '''

        try:
            
            main_database = database
            conversations_collection = main_database[CHAT_COLLECTION_NAME]
            user_email = user["email"]
            stored_chats = await get_all_stored_user_chats(email=user_email,conversations_collection=conversations_collection)
            return JSONResponse(content=stored_chats, status_code=200)
        except Exception as e:  
            message =   f"Failed to retrieve stored chats: {e}" 
            logging.error(message) 
            return JSONResponse(content={"message":message}, status_code=500)
    
    return router