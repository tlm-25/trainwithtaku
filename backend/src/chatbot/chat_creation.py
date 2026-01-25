from src.schemas import Conversation
from src.config import CHAT_COLLECTION_NAME



from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import uuid
import datetime


async def create_new_chat(email:str,database:AsyncDatabase):
    pass


        


