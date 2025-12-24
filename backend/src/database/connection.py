from pymongo import AsyncMongoClient
import os 
from src.config import MONGO_DB_CONNECTION_STRING


MONGO_CLIENT = AsyncMongoClient(host=MONGO_DB_CONNECTION_STRING)

