#upload files to vector database

from src.config import APP_CONFIG
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name
OPENAI_API_KEY = APP_CONFIG.chatbot.openai_api_key.get_secret_value()
EMBEDDING_MODEL_NAME = APP_CONFIG.chatbot.embedding_model_name
from src.database.connection import create_or_get_database
from src.database.document_source_validation import check_valid_url_format, check_valid_pdf_path_format

from src.search.embeddings import get_embedding_model
from pymongo.asynchronous.database import AsyncDatabase

from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.schema import Document

import asyncio

#function for splitting the text int chunks
TEXT_SPLITTER = RecursiveCharacterTextSplitter(

    #maximum size of chunk, measured with length function
    chunk_size= 1000,
    #target overlap between chunks - help mitigate loss of information when context divided
    chunk_overlap = 20,

    #function for determining chunk size
    length_function =len

)




  
async def generate_documents(source_type:str,url:str=None,pdf_path:str=None)->list[Document]:
    '''
        Generating documents to be uploaded to the vector store
        
        :param source: source of the documents 'web' or 'pdf'
        :type source: str
        :param url: url of the web page to be loaded if source is 'web'
        :param pdf_path: path to the pdf file to be loaded if source is 'pdf'
        :return: list of documents
        :rtype: list[Document]
    
    '''
    
    
    doc_source = source_type.lower()
    
    #if source is web page
    if doc_source == "web":
        if url is None:
            raise ValueError("if source is web, 'url' parameter must be set")
        
        #checking if url format is invdalid
        if not check_valid_url_format(url):
            raise ValueError("invalid url format")
        
        web_loader = WebBaseLoader(url)
        docs = web_loader.load_and_split(TEXT_SPLITTER)
        return docs
        
    #if source is a pdf file 
    if doc_source == "pdf":
        if pdf_path is None:
            raise ValueError("if source is pdf, 'pdf_path' parameter must be set")
        #checking if pdf file path format is invalid
        if not check_valid_pdf_path_format(pdf_path):
            raise ValueError("invalid pdf file path format")
         
        pdf_loader = PyPDFLoader(pdf_path)
        docs = pdf_loader.load_and_split(TEXT_SPLITTER)
        return docs
  
    else:
        raise ValueError("source must be either 'web' or 'pdf'")

async def upload_to_vector_store(database:AsyncDatabase,documents:list[Document],collection_name:str):
    embeddings = await get_embedding_model()
    vector_store_collection = database[collection_name]

    document_data = []
    for document in documents:

        # Generate embedding for each document
        embedding = embeddings.embed_documents([document.page_content])
        # Add embedding to document metadata

        document_data.append({

            "content": document.page_content,
            "embedding": embedding[0],
            "source": document.metadata.get("source","")

        })

    #upload to vector store
    vector_upload = await vector_store_collection.insert_many(document_data)
    
    return "successfully uploaded documents"