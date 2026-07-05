from src.database.connection import create_or_get_database
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pymongo.asynchronous.database import AsyncDatabase
from slowapi import Limiter
from src.config import APP_CONFIG as config
from google.cloud import storage
# using third party library to get async functionality with gcloud storage
# documentation https://talkiq.github.io/gcloud-aio/autoapi/storage/index.html
from gcloud.aio.storage import Storage
import aiohttp 

def create_blog_router()->APIRouter:
    '''
    Factory function for creating blog router with an injected rate limiter.
    :return: APIRouter with all auth endpoints registered
    :rtype: APIRouter
    '''
    router = APIRouter(prefix="/api")

    @router.post("/upload_blog")
    async def upload_blog(
        headline_image_file:UploadFile = File(default=None),
        article_id:int = Form(...),
        title:str = Form(...),
        article_text:str = Form(...),
        database:AsyncDatabase=Depends(create_or_get_database)
    ):
        blog_collection_name = config.blogs.blog_collection_name
        
        # get the collection for blogs from database
        main_database = database
        article_info_collection = main_database[blog_collection_name]

        # if image uploaded, save it to google cloud storage
        # client = storage.client()
        # if article has an associate image upload to google cloud and get the image url
        if headline_image_file:

            # create a client for google cloud storage
            # client = storage.Client()

            with aiohttp.ClientSession() as session:
                client = Storage(session=session)
                            # upload the image to google cloud storage
                # get the bucket name from config
                bucket_name = config.blogs.bucket_name
                
                # read raw file bytes
                file_bytes = await headline_image_file.read()

                upload_url = f"https://storage.googleapis.com/{bucket_name}/{headline_image_file.filename}"
                


                status = await client.upload(bucket= bucket_name,object_name=headline_image_file.filename,data=file_bytes)

            


        # get the image url from google cloud storage 

        # save the blog info into mongodb database
        

    return router
