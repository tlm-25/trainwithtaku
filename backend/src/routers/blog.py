from src.database.connection import create_or_get_database
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pymongo.asynchronous.database import AsyncDatabase
from slowapi import Limiter
from src.config import APP_CONFIG as config
from google.cloud import storage
# using third party library to get async functionality with gcloud storage
# documentation https://talkiq.github.io/gcloud-aio/autoapi/storage/index.html
from gcloud.aio.storage import Storage
import aiohttp 
import logging
import uuid 
from datetime import datetime 
import os

logging.basicConfig(level=logging.INFO)

def upload_blog_router()->APIRouter:
    '''
    Factory function for creating blog router with an injected rate limiter.
    :return: APIRouter with all auth endpoints registered
    :rtype: APIRouter
    '''
    router = APIRouter(prefix="/api")

    @router.post("/upload_blog")
    async def upload_blog_router(
        headline_image_file:UploadFile = File(default=None),
        title:str = Form(...),
        article_text:str = Form(...),
        database:AsyncDatabase=Depends(create_or_get_database)
    ):
        blog_collection_name = config.blogs.blog_collection_name
        
        # get the collection for blogs from database
        main_database = database
        article_info_collection = main_database[blog_collection_name]
        
        # Random string for article id
        article_id = str(uuid.uuid4())

        current_datetime =  datetime.now()
        current_date_yyyy_mm_dd = datetime.strftime(current_datetime,format="%Y-%m-%d")

        # if image uploaded, save it to google cloud storage
        # client = storage.client()
        # if article has an associate image upload to google cloud and get the image url
        if headline_image_file:

            

            try:
                async with aiohttp.ClientSession() as session:
                    client = Storage(session=session)
                                # upload the image to google cloud storage
                    # get the bucket name from config
                    bucket_name = config.blogs.bucket_name

                    # read raw file bytes
                    file_bytes = await headline_image_file.read()
                    file_name = headline_image_file.filename


                    # upload to cloud storage using gcloud
                    upload_to_gcloud_storage = await client.upload(bucket=bucket_name, object_name=file_name, file_data=file_bytes)
                    logging.info("Uploaded image to gcloud")
                    # get the image url after uploading it to gcloud storage
                    image_gcs_url = upload_to_gcloud_storage["mediaLink"]
            except Exception as e:
                logging.error(f"Failed to upload image to gcloud storage: {e}")
                raise HTTPException(status_code=502, detail="Failed to upload headline image") from e
            
                

            # save the blog info into mongodb database
            blog_info = {
                "article_id": article_id,
                "title": title,
                "article_text": article_text,
                "headline_image_url": image_gcs_url,
                "date":current_date_yyyy_mm_dd
            }


            
        
        else: 
            logging.warning("No image provided")
        
            # save the blog info into mongodb database - use default logo if no image upload image provided
            blog_info = {
                "article_id": article_id,
                "title": title,
                "article_text": article_text,
                "headline_image_url": config.blogs.default_blog_image_url,
                "date": current_date_yyyy_mm_dd
            }


        # insert the blog info to the mongo db collection
        try:
            await article_info_collection.insert_one(blog_info)
            logging.info("Uploaded blog to mongodb")
        except Exception as e:
            logging.error(f"Failed to save blog to mongodb: {e}")
            raise HTTPException(status_code=500, detail="Failed to save blog post") from e

        
        
        return JSONResponse(content={"message":"Blog uploaded successfully"},status_code=200)
    

    @router.get("/blogs")
    async def fetch_blogs(
        page: int = 1,
        limit: int = 10,
        database: AsyncDatabase = Depends(create_or_get_database)
    ):
        blog_collection_name = config.blogs.blog_collection_name
        article_info_collection = database[blog_collection_name]

        skip = (page - 1) * limit

        # pagination - get the "next" 10 items, ordered by date by default
        cursor = article_info_collection.find().sort("date", -1).skip(skip).limit(limit)
        blogs = await cursor.to_list(length=limit)

        # get total number of artucles
        total_count = await article_info_collection.count_documents({})

        for blog in blogs:
            blog["_id"] = str(blog["_id"])

        return JSONResponse(content={
            "blogs": blogs,
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": (total_count + limit - 1) // limit
        }, status_code=200)
            

    return router


