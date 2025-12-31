from src.database.vector_store import generate_documents
from src.database.document_source_validation import check_valid_url_format, check_valid_pdf_path_format

from langchain.schema import Document

import pytest

@pytest.mark.asyncio
async def test_success_generate_web_docs():
    '''
        Test for successful generation of documents from a web page
    '''
    url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4090010/"

    documents = await generate_documents(source_type="web",url=url)
    assert len(documents) > 0
    assert isinstance(documents[0],Document)

@pytest.mark.asyncio
async def test_invalid_url_format():
    '''
        Test handling of invalid URL format
        
    '''

    invalid_url = "htps://www.google.com"
    with pytest.raises(ValueError,match="invalid url format"):
        await generate_documents(source_type="web",url=invalid_url)

@pytest.mark.asyncio
async def test_success_generate_pdf_docs():
    '''
        Test for successful generation of documents from a pdf document
    '''
    pdf_path = "pdf_documents/twt_hench_head_start.pdf"

    documents = await generate_documents(source_type="pdf",pdf_path=pdf_path)
    print(type(documents))
    print(documents)
    assert len(documents) > 0
    assert isinstance(documents[0],Document)

@pytest.mark.asyncio
async def test_invalid_pdf_extension():
    '''
        Test handling of invalid pdf file format   
    '''

    invalid_path = "pdf_documents/twt_hench_head_start.txt"
    #check that correct error message raised 
    with pytest.raises(ValueError,match="invalid pdf file path format"):
        await generate_documents(source_type="pdf",pdf_path=invalid_path)
