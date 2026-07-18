from src.database.vector_store import generate_documents, upload_to_vector_store
from src.config import APP_CONFIG
DATABASE_NAME = APP_CONFIG.database.database_name
VECTOR_STORE_COLLECTION_NAME = APP_CONFIG.database.vector_store_collection_name

#script for uploading documents to vector store collection in the database
from src.database.connection import create_or_get_database

from langchain.schema import Document
from pymongo.asynchronous.database import AsyncDatabase
import asyncio


async def upload_pdf_to_database(file_path:str):
    mongo_database = await create_or_get_database().__anext__()
    
    documents = await generate_documents(source_type="pdf",pdf_path=file_path)
    response = await upload_to_vector_store(database=mongo_database,documents=documents,collection_name=VECTOR_STORE_COLLECTION_NAME)

    print(response)

async def upload_web_source_to_database(url:str):
    mongo_database = await create_or_get_database().__anext__()
    
    documents = await generate_documents(source_type="web",url=url)
    response = await upload_to_vector_store(database=mongo_database,documents=documents,collection_name=VECTOR_STORE_COLLECTION_NAME)

    print(response)

# asyncio.run(upload_pdf_to_database(file_path="pdf_documents/twt_hench_head_start.pdf"))
asyncio.run(upload_web_source_to_database(url="https://pmc.ncbi.nlm.nih.gov/articles/PMC4090010/"))


### UPLOADED DOCUMENTS SO FAR: SEE BELOW
# pdf_documents/improve_pull_ups.pdf - DONE
# pdf_documents/twt_hench_head_start.pdf - DONE
# https://pmc.ncbi.nlm.nih.gov/articles/PMC4090010/ - DONE
# https://www.strongerbyscience.com/reps-percentage/ - DONE
# https://jeffnippard.com/blogs/news/how-many-sets-do-you-need - DONE
# https://jeffnippard.com/blogs/news/the-best-science-based-minimalist-workout-plan-under-45-mins - DONE
#https://alexleonidas.com/alpha-destiny-novice-intermediate-hybrid-program" - DONE
# https://www.strongerbyscience.com/periodization-data/ - DONE
# https://jeffnippard.com/blogs/news/how-to-build-muscle-and-lose-fat-at-the-same-time-step-by-step-explained-body-recomposition - DONE
# https://www.nhs.uk/live-well/eat-well/food-types/different-fats-nutrition/#:~:text=Saturated%20fat%20guidelines&text=The%20government%20recommends%20that%3A,of%20saturated%20fat%20a%20day - DONE